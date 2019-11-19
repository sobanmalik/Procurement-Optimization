#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from pulp import *
bmo_materials=pd.read_csv('C:/Users/hp/Documents/bmo_materials_model.csv',encoding='UTF-8')
bmo_materials.loc[bmo_materials['Ash'].isna(),'Ash']=0
bmo_materials.loc[bmo_materials['Material']=='Coke (Purchase)','Cost/MT']=30000
bmo_materials


# In[2]:


no_of_days_planned=1
no_of_days_in_a_month=31
capacity_input=pd.read_csv('C:/Users/hp/Documents/Capacity Input bmo model.csv')
capacity_input['Plan Period']=capacity_input['Monthly ']*no_of_days_planned/no_of_days_in_a_month
capacity_input.round(1)


# In[3]:


inventory_bmo=pd.read_csv('C:/Users/hp/Documents/inventory_bmo_model.csv')
inventory_bmo['Return Fines (%)']=inventory_bmo['Return Fines (%)'].str.replace('%','').astype(float)
inventory_bmo['Net Inventory (in MT)']=inventory_bmo['Gross Inventory/day (in MT)']*(1-(inventory_bmo['Return Fines (%)']/100))*no_of_days_planned
inventory_bmo


# In[4]:


pellet_cost_calculation=pd.read_csv('C:/Users/hp/Documents/pellet_cost_model.csv')
pellet_cost_calculation['INR/Ton']=pellet_cost_calculation['INR/Ton'].str.replace('-','0').astype(float)
pellet_cost_calculation


# In[5]:


sinter_cost_calculation=pd.read_csv('C:/Users/hp/Documents/sinter_cost_model.csv')
sinter_cost_calculation['INR/Ton']=sinter_cost_calculation['INR/Ton'].replace('-','0').astype(float)
sinter_cost_calculation


# In[6]:


#Costing Data
pellet_current_cost=6958
pellet_current_production=capacity_input.loc[capacity_input['material']=='Pellet','Plan Period'].item()+capacity_input.loc[capacity_input['material']=='Flux Pellet','Plan Period'].item()
pellet_tfc=pellet_current_production*pellet_cost_calculation.loc[pellet_cost_calculation['Pellet Plant']=='Total Fixed Cost','INR/Ton'].item()
pellet_excel_fixed_cost=pellet_current_cost-pellet_cost_calculation.loc[pellet_cost_calculation['Pellet Plant']=='Total Fixed Cost','INR/Ton'].item()
pellet_new_cost=(pellet_tfc/capacity_input.loc[capacity_input['material']=='Pellet','Plan Period'].item())+pellet_excel_fixed_cost
pellet_new_cost


# In[7]:


#Costing Data
sinter_current_cost=4382
sinter_current_production=capacity_input.loc[capacity_input['material']=='Sinter (considering return fines)','Plan Period'].item()
sinter_tfc=sinter_current_production*sinter_cost_calculation.loc[sinter_cost_calculation['Sinter Plant']=='Total Fixed Cost','INR/Ton'].item()
sinter_excel_fixed_cost=sinter_current_cost-sinter_cost_calculation.loc[sinter_cost_calculation['Sinter Plant']=='Total Fixed Cost','INR/Ton'].item()
sinter_new_cost=(sinter_tfc/inventory_bmo.loc[inventory_bmo['RM (for daily planning)']=='Sinter','Net Inventory (in MT)'].item())+sinter_excel_fixed_cost
sinter_new_cost


# In[8]:


bmo_materials.loc[bmo_materials['Material']=='Sinter','Cost/MT']=[sinter_new_cost]
bmo_materials.loc[bmo_materials['Material']=='Pellet','Cost/MT']=[pellet_new_cost]
bmo_materials.round(1)


# In[9]:


model=LpProblem('BMO optimisation',LpMaximize)
var_bmo_P2_bf1=LpVariable.dicts('BMO Material quantity in Tons P2 BF1',bmo_materials['Material'],0,None,LpContinuous) 
var_bmo_P2_bf2=LpVariable.dicts('BMO Material quantity in Tons P2 BF2',bmo_materials['Material'],0,None,LpContinuous)


# In[11]:


model.variables()


# In[10]:


zxc=list()
#Inventory Constraints
for i in inventory_bmo['RM (for daily planning)']:
    model+=lpSum(var_bmo_P2_bf1[i]+var_bmo_P2_bf2[i])<=inventory_bmo.loc[inventory_bmo['RM (for daily planning)']==i,'Net Inventory (in MT)'].item()


# In[11]:


#updating P2 chemistry values
#Feeding DMT
bmo_feeding_dmt_list_P2_bf1=list()
for i in bmo_materials['Material']:
    x=bmo_materials.loc[bmo_materials['Material']==i,'Moi'].item()*var_bmo_P2_bf1[i]/100
    bmo_feeding_dmt_list_P2_bf1.append(x)
bmo_materials['feeding_dmt_P2_bf1']=bmo_feeding_dmt_list_P2_bf1

#Fe_new
bmo_fe_list_P2_bf1=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf1[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf1'].item())*bmo_materials.loc[bmo_materials['Material']==i,'Fe'].item()/100
    bmo_fe_list_P2_bf1.append(x)
bmo_materials['Fe(new)_P2_bf1']=bmo_fe_list_P2_bf1

#SiO2_new
bmo_SiO2_list_P2_bf1=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf1[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf1'].item())*bmo_materials.loc[bmo_materials['Material']==i,'SiO2'].item()/100
    bmo_SiO2_list_P2_bf1.append(x)
bmo_materials['SiO2(new)_P2_bf1']=bmo_SiO2_list_P2_bf1
bmo_SiO2_list_P2_bf1

#Al2O3_new
bmo_Al2O3_list_P2_bf1=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf1[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf1'].item())*bmo_materials.loc[bmo_materials['Material']==i,'Al2O3'].item()/100
    bmo_Al2O3_list_P2_bf1.append(x)
bmo_materials['Al2O3(new)_P2_bf1']=bmo_Al2O3_list_P2_bf1

#CaO_new
bmo_CaO_list_P2_bf1=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf1[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf1'].item())*bmo_materials.loc[bmo_materials['Material']==i,'CaO'].item()/100
    bmo_CaO_list_P2_bf1.append(x)
bmo_materials['CaO(new)_P2_bf1']=bmo_CaO_list_P2_bf1

#MgO_new
bmo_MgO_list_P2_bf1=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf1[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf1'].item())*bmo_materials.loc[bmo_materials['Material']==i,'MgO'].item()/100
    bmo_MgO_list_P2_bf1.append(x)
bmo_materials['MgO(new)_P2_bf1']=bmo_MgO_list_P2_bf1

#P_new
bmo_P_list_P2_bf1=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf1[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf1'].item())*bmo_materials.loc[bmo_materials['Material']==i,'P'].item()/100
    bmo_P_list_P2_bf1.append(x)
bmo_materials['P(new)_P2_bf1']=bmo_P_list_P2_bf1


#S_new
bmo_S_list_P2_bf1=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf1[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf1'].item())*bmo_materials.loc[bmo_materials['Material']==i,'S'].item()/100
    bmo_S_list_P2_bf1.append(x)
bmo_materials['S(new)_P2_bf1']=bmo_S_list_P2_bf1


# In[12]:


#updating P2 chemistry values
#Feeding DMT
bmo_feeding_dmt_list_P2_bf2=list()
for i in bmo_materials['Material']:
    x=bmo_materials.loc[bmo_materials['Material']==i,'Moi'].item()*var_bmo_P2_bf2[i]/100
    bmo_feeding_dmt_list_P2_bf2.append(x)
bmo_materials['feeding_dmt_P2_bf2']=bmo_feeding_dmt_list_P2_bf2

#Fe_new
bmo_fe_list_P2_bf2=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf2[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf2'].item())*bmo_materials.loc[bmo_materials['Material']==i,'Fe'].item()/100
    bmo_fe_list_P2_bf2.append(x)
bmo_materials['Fe(new)_P2_bf2']=bmo_fe_list_P2_bf2

#SiO2_new
bmo_SiO2_list_P2_bf2=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf2[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf2'].item())*bmo_materials.loc[bmo_materials['Material']==i,'SiO2'].item()/100
    bmo_SiO2_list_P2_bf2.append(x)
bmo_materials['SiO2(new)_P2_bf2']=bmo_SiO2_list_P2_bf2
bmo_SiO2_list_P2_bf2

#Al2O3_new
bmo_Al2O3_list_P2_bf2=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf2[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf2'].item())*bmo_materials.loc[bmo_materials['Material']==i,'Al2O3'].item()/100
    bmo_Al2O3_list_P2_bf2.append(x)
bmo_materials['Al2O3(new)_P2_bf2']=bmo_Al2O3_list_P2_bf2

#CaO_new
bmo_CaO_list_P2_bf2=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf2[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf2'].item())*bmo_materials.loc[bmo_materials['Material']==i,'CaO'].item()/100
    bmo_CaO_list_P2_bf2.append(x)
bmo_materials['CaO(new)_P2_bf2']=bmo_CaO_list_P2_bf2

#MgO_new
bmo_MgO_list_P2_bf2=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf2[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf2'].item())*bmo_materials.loc[bmo_materials['Material']==i,'MgO'].item()/100
    bmo_MgO_list_P2_bf2.append(x)
bmo_materials['MgO(new)_P2_bf2']=bmo_MgO_list_P2_bf2

#P_new
bmo_P_list_P2_bf2=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf2[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf2'].item())*bmo_materials.loc[bmo_materials['Material']==i,'P'].item()/100
    bmo_P_list_P2_bf2.append(x)
bmo_materials['P(new)_P2_bf2']=bmo_P_list_P2_bf2


#S_new
bmo_S_list_P2_bf2=list()
for i in bmo_materials['Material']:
    x=(var_bmo_P2_bf2[i]-bmo_materials.loc[bmo_materials['Material']==i,'feeding_dmt_P2_bf2'].item())*bmo_materials.loc[bmo_materials['Material']==i,'S'].item()/100
    bmo_S_list_P2_bf2.append(x)
bmo_materials['S(new)_P2_bf2']=bmo_S_list_P2_bf2


# In[13]:


#values cell
pellet_production=650000
DRI=150000
values_P2=pd.read_csv('C:/Users/hp/Documents/Values P2.csv')
#values_P2_bf2=pd.read_csv('C:/Users/hp/Documents/Values P2 BF2.csv')
values_P2


# In[14]:


#P2_bf1_ Chemistry Totals (Integration part)
Fe_total_P2_bf1=lpSum([bmo_materials['Fe(new)_P2_bf1']])
SiO2_total_P2_bf1=lpSum([bmo_materials['SiO2(new)_P2_bf1']])
Al2O3_total_P2_bf1=lpSum([bmo_materials['Al2O3(new)_P2_bf1']])
CaO_total_P2_bf1=lpSum([bmo_materials['CaO(new)_P2_bf1']])
MgO_total_P2_bf1=lpSum([bmo_materials['MgO(new)_P2_bf1']])
P_total_P2_bf1=lpSum([bmo_materials['P(new)_P2_bf1']])
S_total_P2_bf1=lpSum([bmo_materials['S(new)_P2_bf1']])

#Si_total(using Fe)
Si_total_P2_bf1=(Fe_total_P2_bf1*99/95)*values_P2.loc[values_P2['Parameter']=='Si %','Value'].item()/100

#Kg/Thm
Kg_by_Thm_P2_bf1=Fe_total_P2_bf1*99/95


# In[15]:


#P2_bf2_ Chemistry Totals (Integration part)
Fe_total_P2_bf2=lpSum([bmo_materials['Fe(new)_P2_bf2']])
SiO2_total_P2_bf2=lpSum([bmo_materials['SiO2(new)_P2_bf2']])
Al2O3_total_P2_bf2=lpSum([bmo_materials['Al2O3(new)_P2_bf2']])
CaO_total_P2_bf2=lpSum([bmo_materials['CaO(new)_P2_bf2']])
MgO_total_P2_bf2=lpSum([bmo_materials['MgO(new)_P2_bf2']])
P_total_P2_bf2=lpSum([bmo_materials['P(new)_P2_bf2']])
S_total_P2_bf2=lpSum([bmo_materials['S(new)_P2_bf2']])

#Si_total(using Fe)
Si_total_P2_bf2=(Fe_total_P2_bf2*99/95)*values_P2.loc[values_P2['Parameter']=='Si %','Value'].item()/100

#Kg/Thm
Kg_by_Thm_P2_bf2=Fe_total_P2_bf2*99/95


# In[16]:


#bmo chemistry constraints input
bmo_chemistry_table_P2_bf1=pd.read_csv('C:/Users/hp/Documents/BMO chemsitry constraints P2 bf1.csv')
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Min'].isna(),'Min']=0
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Max'].isna(),'Max']=0


# In[17]:


#bmo chemistry constraints input
bmo_chemistry_table_P2_bf2=pd.read_csv('C:/Users/hp/Documents/BMO chemistry constraints raigar bf2.csv')
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Min'].isna(),'Min']=0
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Max'].isna(),'Max']=0


# In[18]:


# P2_bf1
#bmo_chemistry_constraints
#updating min(total)_P2_bf1
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='FE (Kg/THM)','min(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='FE (Kg/THM)','Min'].item()*Kg_by_Thm_P2_bf1]
#bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Basicity (B1)','min(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Basicity (B1)','Min'].item()*P_total_P2_bf1]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Amount','min(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Amount','Min'].item()*Kg_by_Thm_P2_bf1]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Phosphorus','min(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Phosphorus','Min'].item()*Kg_by_Thm_P2_bf1]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='MgO','min(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='MgO','Min'].item()*(CaO_total_P2_bf1+MgO_total_P2_bf1+(SiO2_total_P2_bf1-(Si_total_P2_bf1/0.466))+Al2O3_total_P2_bf1)/(bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='FE (Kg/THM)','Min'].item()/1000)]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Al2O3','min(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Al2O3','Min'].item()*(CaO_total_P2_bf1+MgO_total_P2_bf1+(SiO2_total_P2_bf1-(Si_total_P2_bf1/0.466))+Al2O3_total_P2_bf1)/(bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='FE (Kg/THM)','Min'].item()/1000)]

#updating max(total)_P2_bf1
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Amount','max(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Amount','Max'].item()*Kg_by_Thm_P2_bf1]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Sulphur in HM','max(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Sulphur in HM','Max'].item()*Kg_by_Thm_P2_bf1/100000]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Phosphorus','max(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Phosphorus','Max'].item()*Kg_by_Thm_P2_bf1]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='MgO','max(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='MgO','Max'].item()*(CaO_total_P2_bf1+MgO_total_P2_bf1+(SiO2_total_P2_bf1-(Si_total_P2_bf1/0.466))+Al2O3_total_P2_bf1)/(bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='FE (Kg/THM)','Min'].item()/1000)]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Al2O3','max(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Al2O3','Max'].item()*(CaO_total_P2_bf1+MgO_total_P2_bf1+(SiO2_total_P2_bf1-(Si_total_P2_bf1/0.466))+Al2O3_total_P2_bf1)/(bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='FE (Kg/THM)','Min'].item()/1000)]


# In[19]:


#P2_bf2
#bmo_chemistry_constraints
#updating min(total)_P2_bf2
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='FE (Kg/THM)','min(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='FE (Kg/THM)','Min'].item()*Kg_by_Thm_P2_bf2]
#bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Basicity (B1)','min(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Basicity (B1)','Min'].item()*P_total_P2_bf2]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Amount','min(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Amount','Min'].item()*Kg_by_Thm_P2_bf2]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Phosphorus','min(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Phosphorus','Min'].item()*Kg_by_Thm_P2_bf2]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='MgO','min(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='MgO','Min'].item()*(CaO_total_P2_bf2+MgO_total_P2_bf2+(SiO2_total_P2_bf2-(Si_total_P2_bf2/0.466))+Al2O3_total_P2_bf2)/(bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='FE (Kg/THM)','Min'].item()/1000)]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Al2O3','min(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Al2O3','Min'].item()*(CaO_total_P2_bf2+MgO_total_P2_bf2+(SiO2_total_P2_bf2-(Si_total_P2_bf2/0.466))+Al2O3_total_P2_bf2)/(bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='FE (Kg/THM)','Min'].item()/1000)]

#updating max(total)_P2_bf2
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Amount','max(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Amount','Max'].item()*Kg_by_Thm_P2_bf2]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Sulphur in HM','max(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Sulphur in HM','Max'].item()*Kg_by_Thm_P2_bf2/100000]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Phosphorus','max(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Phosphorus','Max'].item()*Kg_by_Thm_P2_bf2]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='MgO','max(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='MgO','Max'].item()*(CaO_total_P2_bf2+MgO_total_P2_bf2+(SiO2_total_P2_bf2-(Si_total_P2_bf2/0.466))+Al2O3_total_P2_bf2)/(bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='FE (Kg/THM)','Min'].item()/1000)]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Al2O3','max(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Al2O3','Max'].item()*(CaO_total_P2_bf2+MgO_total_P2_bf2+(SiO2_total_P2_bf2-(Si_total_P2_bf2/0.466))+Al2O3_total_P2_bf2)/(bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='FE (Kg/THM)','Min'].item()/1000)]


# In[20]:


#P2_bf1
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='FE (Kg/THM)','Actual Values_P2_bf1']=[Fe_total_P2_bf1*1000]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Amount','Actual Values_P2_bf1']=[((CaO_total_P2_bf1+MgO_total_P2_bf1+(SiO2_total_P2_bf1-(Si_total_P2_bf1/0.466))+Al2O3_total_P2_bf1)/(bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='FE (Kg/THM)','Min'].item()/1000))*1000]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Sulphur in HM','Actual Values_P2_bf1']=[(S_total_P2_bf1/1000)-0.217]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Phosphorus','Actual Values_P2_bf1']=[P_total_P2_bf1*100]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='CaO','Actual Values_P2_bf1']=[(CaO_total_P2_bf1-(56/32*0.7*(CaO_total_P2_bf1+MgO_total_P2_bf1+(SiO2_total_P2_bf1-(Si_total_P2_bf1/0.466))+Al2O3_total_P2_bf1)/(bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='FE (Kg/THM)','Min'].item()/1000)/100))*100]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='MgO','Actual Values_P2_bf1']=[MgO_total_P2_bf1*100]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='SiO2','Actual Values_P2_bf1']=[(SiO2_total_P2_bf1-(Si_total_P2_bf1/0.466))*100]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Al2O3','Actual Values_P2_bf1']=[Al2O3_total_P2_bf1*100]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Basicity (B1)','Actual Values_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='CaO','Actual Values_P2_bf1'].item()]


# In[21]:


#P2_bf2
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='FE (Kg/THM)','Actual Values_P2_bf2']=[Fe_total_P2_bf2*1000]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Amount','Actual Values_P2_bf2']=[((CaO_total_P2_bf2+MgO_total_P2_bf2+(SiO2_total_P2_bf2-(Si_total_P2_bf2/0.466))+Al2O3_total_P2_bf2)/(bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='FE (Kg/THM)','Min'].item()/1000))*1000]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Sulphur in HM','Actual Values_P2_bf2']=[(S_total_P2_bf2/1000)-0.217]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Phosphorus','Actual Values_P2_bf2']=[P_total_P2_bf2*100]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='CaO','Actual Values_P2_bf2']=[(CaO_total_P2_bf2-(56/32*0.7*(CaO_total_P2_bf2+MgO_total_P2_bf2+(SiO2_total_P2_bf2-(Si_total_P2_bf2/0.466))+Al2O3_total_P2_bf2)/(bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='FE (Kg/THM)','Min'].item()/1000)/100))*100]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='MgO','Actual Values_P2_bf2']=[MgO_total_P2_bf2*100]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='SiO2','Actual Values_P2_bf2']=[(SiO2_total_P2_bf2-(Si_total_P2_bf2/0.466))*100]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Al2O3','Actual Values_P2_bf2']=[Al2O3_total_P2_bf2*100]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Basicity (B1)','Actual Values_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='CaO','Actual Values_P2_bf2'].item()]


# In[22]:


#remaining related min/max(total) P2_bf1
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Basicity (B1)','min(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Basicity (B1)','Min'].item()*bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='SiO2','Actual Values_P2_bf1'].item()]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Basicity (B1)','max(total)_P2_bf1']=[bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Slag Basicity (B1)','Max'].item()*bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='SiO2','Actual Values_P2_bf1'].item()]


# In[23]:


#remaining related min/max(total) P2_bf2
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Basicity (B1)','min(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Basicity (B1)','Min'].item()*bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='SiO2','Actual Values_P2_bf2'].item()]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Basicity (B1)','max(total)_P2_bf2']=[bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='Slag Basicity (B1)','Max'].item()*bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']=='SiO2','Actual Values_P2_bf2'].item()]


# In[24]:


#Coke inputs
coke_input_P2_bf1=pd.read_csv('C:/Users/hp/Documents/coke input P2 bf1.csv')

#sinter pellet lump inputs
spl_input_P2_bf1=pd.read_csv('C:/Users/hp/Documents/Sinetr Pellet Lump P2 BF1.csv')
coke_input_P2_bf1


# In[25]:


#Coke inputs
coke_input_P2_bf2=pd.read_csv('C:/Users/hp/Documents/coke input P2 bf2.csv')

#sinter pellet lump inputs
spl_input_P2_bf2=pd.read_csv('C:/Users/hp/Documents/Sinter Pellet Lump P2 BF2.csv')
coke_input_P2_bf1


# In[26]:


bmo_chemistry_table_P2_bf1['key_min']=[1,1,1,0,1,0,1,0,1]
bmo_chemistry_table_P2_bf1['key_max']=[0,0,1,0,1,0,1,0,0]
bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['min(total)_P2_bf1'].isna(),'min(total)_P2_bf1']=0

bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['max(total)_P2_bf1'].isna(),'max(total)_P2_bf1']=0


# In[27]:


bmo_chemistry_table_P2_bf2['key_min']=[1,1,1,0,1,0,1,0,1]
bmo_chemistry_table_P2_bf2['key_max']=[0,0,1,0,1,0,1,0,0]
bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['min(total)_P2_bf2'].isna(),'min(total)_P2_bf2']=0

bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['max(total)_P2_bf2'].isna(),'max(total)_P2_bf2']=0


# In[28]:


#output(bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Al2O3','Actual Values_P2_bf1'])


# In[29]:


#output(bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']=='Al2O3','max(total)_P2_bf1'].item())


# In[30]:


zxc=list()
#P2_bf1
for i in bmo_chemistry_table_P2_bf1['Parameters']:
    if bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']==i,'key_min'].item()==1:
        a=bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']==i,'Actual Values_P2_bf1'].item()>=bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']==i,'min(total)_P2_bf1'].item()
        model+=a
for i in bmo_chemistry_table_P2_bf1['Parameters']:
    if bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']==i,'key_max'].item()==1:
        a=bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']==i,'Actual Values_P2_bf1'].item()<=bmo_chemistry_table_P2_bf1.loc[bmo_chemistry_table_P2_bf1['Parameters']==i,'max(total)_P2_bf1'].item()        
        model+=a                


# In[31]:


#P2_bf2
for i in bmo_chemistry_table_P2_bf2['Parameters']:
    if bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']==i,'key_min'].item()==1:
        a=bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']==i,'Actual Values_P2_bf2'].item()>=bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']==i,'min(total)_P2_bf2'].item()
        model+=a
for i in bmo_chemistry_table_P2_bf2['Parameters']:
    if bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']==i,'key_max'].item()==1:
        a=bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']==i,'Actual Values_P2_bf2'].item()<=bmo_chemistry_table_P2_bf2.loc[bmo_chemistry_table_P2_bf2['Parameters']==i,'max(total)_P2_bf2'].item()       
        model+=a                


# In[32]:


#total_production constraint
#P2
#model+=lpSum(Kg_by_Thm_P2_bf1)>=values_P2.loc[values_P2['Parameter']=='Total Production','Value'].item()*no_of_days_planned/no_of_days_in_a_month


# In[33]:


#total_production constraint
#P2
#model+=lpSum(Kg_by_Thm_P2_bf2)>=values_P2.loc[values_P2['Parameter']=='Total Production','Value'].item()*no_of_days_planned/no_of_days_in_a_month


# In[34]:


spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Sinter','Actual']=[var_bmo_P2_bf1['Sinter']]
spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Pellet','Actual']=[var_bmo_P2_bf1['Pellet']]
spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Lump','Actual']=[var_bmo_P2_bf1['Lump']]
total_ibm_P2_bf1=lpSum(spl_input_P2_bf1['Actual'])
#updating min 
for i in spl_input_P2_bf1['Parameter']:
    spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']==i,'min(wtd)']=[total_ibm_P2_bf1*spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']==i,'Min'].item()]
#updating max
for i in spl_input_P2_bf1['Parameter']:
    spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']==i,'max(wtd)']=[total_ibm_P2_bf1*spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']==i,'Max'].item()]
    
for i in spl_input_P2_bf1['Parameter']:
    a=spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']==i,'Actual'].item()<=spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']==i,'max(wtd)'].item()        
    model+=a  
    
for i in spl_input_P2_bf1['Parameter']:
    a=spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']==i,'Actual'].item()>=spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']==i,'min(wtd)'].item()        
    model+=a   
    


# In[35]:


spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Sinter','Actual']=[var_bmo_P2_bf2['Sinter']]
spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Pellet','Actual']=[var_bmo_P2_bf2['Pellet']]
spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Lump','Actual']=[var_bmo_P2_bf2['Lump']]
total_ibm_P2_bf2=lpSum(spl_input_P2_bf2['Actual'])
#updating min 
for i in spl_input_P2_bf2['Parameter']:
    spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']==i,'min(wtd)']=[total_ibm_P2_bf2*spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']==i,'Min'].item()]
#updating max
for i in spl_input_P2_bf2['Parameter']:
    spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']==i,'max(wtd)']=[total_ibm_P2_bf2*spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']==i,'Max'].item()]
    
for i in spl_input_P2_bf2['Parameter']:
    a=spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']==i,'Actual'].item()<=spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']==i,'max(wtd)'].item()        
    model+=a  
    
for i in spl_input_P2_bf2['Parameter']:
    a=spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']==i,'Actual'].item()>=spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']==i,'min(wtd)'].item()        
    model+=a      
    
    


# In[36]:


spl_input_P2_bf1


# In[37]:


#P2_bf1
for i in coke_input_P2_bf1['Parameter']:
    coke_input_P2_bf1.loc[coke_input_P2_bf1['Parameter']==i,'Actual']=[Kg_by_Thm_P2_bf1*coke_input_P2_bf1.loc[coke_input_P2_bf1['Parameter']==i,'Limit'].item()/1000]

for i in coke_input_P2_bf1['Parameter']:
    model+=lpSum(var_bmo_P2_bf1[i])>=coke_input_P2_bf1.loc[coke_input_P2_bf1['Parameter']==i,'Actual'].item()
    


# In[38]:


#P2_bf2
for i in coke_input_P2_bf2['Parameter']:
    coke_input_P2_bf2.loc[coke_input_P2_bf2['Parameter']==i,'Actual']=[Kg_by_Thm_P2_bf2*coke_input_P2_bf2.loc[coke_input_P2_bf2['Parameter']==i,'Limit'].item()/1000]

for i in coke_input_P2_bf2['Parameter']:
    model+=lpSum(var_bmo_P2_bf2[i])>=coke_input_P2_bf2.loc[coke_input_P2_bf2['Parameter']==i,'Actual'].item()
    


# In[39]:


values_P2['BF1']=values_P2['Value']
values_P2['BF2']=values_P2['Value']
values_P2.iloc[5,2]=8
values_P2.iloc[5,3]=8
#values_P2.iloc[5,3]=8.4
values_P2.iloc[1,2]=24000
values_P2.iloc[1,3]=24000
values_P2.iloc[4,2]=34
values_P2.iloc[4,3]=52

values_P2


# In[40]:


#charge capacity_constraint bf1
total_volume_bf1=28000
#model+=lpSum(var_bmo_P2_bf1)<=total_volume_bf1
coke_rate_bf1=6000
#model+=lpSum(var_bmo_P2_bf1['Coke (c1)']+var_bmo_P2_bf1['Coke (Purchase)'])<=coke_rate_bf1
ibm_and_fixtures_bf1=24000
#model+=lpSum(var_bmo_P2_bf1-var_bmo_P2_bf1['Coke (c1)']-var_bmo_P2_bf1['Coke (Purchase)']-var_bmo_P2_bf1['PCI'])<=ibm_and_fixtures_bf1
#charge_capacity_P2=(spl_input_P2.loc[spl_input_P2['Parameter']=='Sinter','Actual'].item()+spl_input_P2.loc[spl_input_P2['Parameter']=='Pellet','Actual'].item()+spl_input_P2.loc[spl_input_P2['Parameter']=='Lump','Actual'].item()+lpSum(var_bmo_P2))/(values_P2.loc[values_P2['Parameter']=='Charge rate','Value'].item()*no_of_days*24)
#model+=charge_capacity_P2<=values_P2.loc[values_P2['Parameter']=='Charge Capacity','Value'].item()


# In[41]:


charge_capacity_P2_bf1=(lpSum(var_bmo_P2_bf1))/(values_P2.loc[values_P2['Parameter']=='Charge rate','BF1'].item()*no_of_days_planned*24)
#model+=charge_capacity_P2_bf1<=values_P2.loc[values_P2['Parameter']=='Charge Capacity','BF1'].item()


# In[42]:


#charge capacity metallic BFs
charge_capacity_P2_metallic_bf1=((lpSum(var_bmo_P2_bf1[i] for i in bmo_materials['Material'][:3])+lpSum(var_bmo_P2_bf1[i] for i in bmo_materials['Material'][7:10])
                                       +lpSum(var_bmo_P2_bf1['Coke (Nut)']))/(values_P2.loc[values_P2['Parameter']=='Charge rate','BF1'].item()*no_of_days_planned*24))
model+=charge_capacity_P2_metallic_bf1<=28

charge_capacity_P2_metallic_bf2=((lpSum(var_bmo_P2_bf2[i] for i in bmo_materials['Material'][:3])+lpSum(var_bmo_P2_bf2[i] for i in bmo_materials['Material'][7:10])
                                       +lpSum(var_bmo_P2_bf2['Coke (Nut)']))/(values_P2.loc[values_P2['Parameter']=='Charge rate','BF2'].item()*no_of_days_planned*24))
model+=charge_capacity_P2_metallic_bf2<=42


# In[43]:


charge_capacity_P2_metallic_bf2.value()


# In[44]:


#Charge Capacity Fuel BFs
charge_capacity_P2_fuel_bf1=(lpSum(var_bmo_P2_bf1['Coke (c1)'])+lpSum(var_bmo_P2_bf1['Coke (Purchase)']))/(values_P2.loc[values_P2['Parameter']=='Charge rate','BF1'].item()*no_of_days_planned*24)
model+=charge_capacity_P2_fuel_bf1<=6

charge_capacity_P2_fuel_bf2=(lpSum(var_bmo_P2_bf2['Coke (c1)'])+lpSum(var_bmo_P2_bf2['Coke (Purchase)']))/(values_P2.loc[values_P2['Parameter']=='Charge rate','BF2'].item()*no_of_days_planned*24)
model+=charge_capacity_P2_fuel_bf2<=10.5


# In[45]:


#charge capacity total BFs
charge_capacity_P2_total_bf1=((lpSum(var_bmo_P2_bf1[i] for i in bmo_materials['Material'][:3])+lpSum(var_bmo_P2_bf1[i] for i in bmo_materials['Material'][7:10])
                                       +lpSum(var_bmo_P2_bf1['Coke (Nut)'])+lpSum(var_bmo_P2_bf1['Coke (c1)'])+lpSum(var_bmo_P2_bf1['Coke (Purchase)']))/(values_P2.loc[values_P2['Parameter']=='Charge rate','BF1'].item()*no_of_days_planned*24))
model+=charge_capacity_P2_total_bf1<=34

charge_capacity_P2_total_bf2=((lpSum(var_bmo_P2_bf2[i] for i in bmo_materials['Material'][:3])+lpSum(var_bmo_P2_bf2[i] for i in bmo_materials['Material'][7:10])
                                       +lpSum(var_bmo_P2_bf2['Coke (Nut)'])+lpSum(var_bmo_P2_bf2['Coke (c1)'])+lpSum(var_bmo_P2_bf2['Coke (Purchase)']))/(values_P2.loc[values_P2['Parameter']=='Charge rate','BF2'].item()*no_of_days_planned*24))
model+=charge_capacity_P2_total_bf2<=52.5


# In[46]:


#charge capacity_constraint bf2
total_volume_bf2=52000
#model+=lpSum(var_bmo_P2_bf2)<=total_volume_bf2
coke_rate_bf2=10000
#model+=lpSum(var_bmo_P2_bf2['Coke (c1)']+var_bmo_P2_bf2['Coke (Purchase)'])<=coke_rate_bf2
ibm_and_fixtures_bf2=39450
#model+=lpSum(var_bmo_P2_bf2-var_bmo_P2_bf2['Coke (c1)']-var_bmo_P2_bf2['Coke (Purchase)']-var_bmo_P2_bf2['PCI'])<=ibm_and_fixtures_bf2
#charge_capacity_P2=(spl_input_P2.loc[spl_input_P2['Parameter']=='Sinter','Actual'].item()+spl_input_P2.loc[spl_input_P2['Parameter']=='Pellet','Actual'].item()+spl_input_P2.loc[spl_input_P2['Parameter']=='Lump','Actual'].item()+lpSum(var_bmo_P2))/(values_P2.loc[values_P2['Parameter']=='Charge rate','Value'].item()*no_of_days*24)
#model+=charge_capacity_P2<=values_P2.loc[values_P2['Parameter']=='Charge Capacity','Value'].item()


# In[47]:


charge_capacity_P2_bf2=(lpSum(var_bmo_P2_bf2))/(values_P2.loc[values_P2['Parameter']=='Charge rate','BF2'].item()*no_of_days_planned*24)
#model+=charge_capacity_P2_bf2<=values_P2.loc[values_P2['Parameter']=='Charge Capacity','BF2'].item()


# In[48]:


#objective
total_hot_metal_mt=(Kg_by_Thm_P2_bf1+Kg_by_Thm_P2_bf2)/1000
realisation_in_cr=total_hot_metal_mt*values_P2.loc[values_P2['Parameter']=='Realization per ton of HM','BF1'].item()/10000000
#pellet
pellet_for_market=(capacity_input.loc[capacity_input['material']=='Pellet','Plan Period'].item()-lpSum((var_bmo_P2_bf1['Pellet']*24*values_P2.loc[values_P2['Parameter']=='Charge rate','BF1'].item()*no_of_days_planned/1000)+(var_bmo_P2_bf2['Pellet']*24*values_P2.loc[values_P2['Parameter']=='Charge rate','BF2'].item()*no_of_days_planned/1000))
                   -capacity_input.loc[capacity_input['material']=='Pellet for DRI+P1','Plan Period'].item()-lpSum((var_bmo_P2_bf1['Flux pellet']*24*values_P2.loc[values_P2['Parameter']=='Charge rate','BF1'].item()*no_of_days_planned/1000)+(var_bmo_P2_bf2['Flux pellet']*24*values_P2.loc[values_P2['Parameter']=='Charge rate','BF2'].item()*no_of_days_planned/1000)))
Realization_of_pellets_to_be_considerd=0
total_cont_pellet=pellet_for_market*Realization_of_pellets_to_be_considerd/10000000


# In[49]:


cost_bf1=lpSum(bmo_materials.loc[bmo_materials['Material']==i,'Cost/MT'].item()*var_bmo_P2_bf1[i]*24*values_P2.loc[values_P2['Parameter']=='Charge rate','BF1'].item()*no_of_days_planned/1000 for i in var_bmo_P2_bf1)
cost_bf2=lpSum(bmo_materials.loc[bmo_materials['Material']==i,'Cost/MT'].item()*var_bmo_P2_bf2[i]*24*values_P2.loc[values_P2['Parameter']=='Charge rate','BF2'].item()*no_of_days_planned/1000 for i in var_bmo_P2_bf2)
cost_bf1_cr=cost_bf1/10000000
cost_bf2_cr=cost_bf2/10000000


# In[50]:


#objective2
total_cost_bf1=(var_bmo_P2_bf1[i]*bmo_materials.loc[bmo_materials['Material']==i,'Cost/MT'].item() for i in var_bmo_P2_bf1)
total_realisation_bf1=Kg_by_Thm_P2_bf1*values_P2.loc[values_P2['Parameter']=='Realization per ton of HM','BF1'].item()
bf1_contribution=total_realisation_bf1-total_cost_bf1

#objective2
total_cost_bf2=(var_bmo_P2_bf2[i]*bmo_materials.loc[bmo_materials['Material']==i,'Cost/MT'].item() for i in var_bmo_P2_bf2)
total_realisation_bf2=Kg_by_Thm_P2_bf2*values_P2.loc[values_P2['Parameter']=='Realization per ton of HM','BF2'].item()
bf2_contribution=total_realisation_bf2-total_cost_bf2


# In[51]:


#Pellet production
pellet_production=inventory_bmo.loc[inventory_bmo['RM (for daily planning)']=='Pellet','Gross Inventory/day (in MT)'].item()
pellet_used_in_bf=spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Pellet','Actual'].item()+spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Pellet','Actual'].item()
model+=pellet_used_in_bf>=0
#DRI=150000/no_of_days_planned
market_sale=pellet_production-(pellet_used_in_bf)
#model+=market_sale>=0
#pellet_contribution_P1=market_sale*values_P1.loc[values_P1['Parameter']=='Realization from pellet Sale','Value'].item()
pellet_contribution=market_sale*values_P2.loc[values_P2['Parameter']=='Realization from pellet Sale','Value'].item()


# In[52]:


inventory_bmo


# In[53]:


model+=bf1_contribution+bf2_contribution+pellet_contribution
#lpSum(var_bmo_P2_bf1)+lpSum(var_bmo_P2_bf2)
#realisation_in_cr+total_cont_pellet-cost_bf1_cr-cost_bf2_cr


# In[55]:


model


# In[56]:


model.variables()


# In[54]:


model.solve()


# In[55]:


model.writeLP('BMO Model.lp')
print("Status:",LpStatus[model.status])
for v in model.variables():
    print(v.name,"",v.varValue)
final_cost=value(model.objective)
print(" Total contributon is ",final_cost)


# In[56]:


def output(self):
    op_list=list()
    for v, coefficient in lpSum(self).items():
        op_list.append(coefficient*v.varValue)
    op_total=lpSum(op_list).value()
    return op_total

#P2_bf1
sinter_P2_bf1=output(spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Sinter','Actual'])
sinter_P2_bf1_max_wtd=output(spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Sinter','max(wtd)'])
sinter_P2_bf1_min_wtd=output(spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Sinter','min(wtd)'])
pellet_P2_bf1=output(spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Pellet','Actual'])
pellet_P2_bf1_max_wtd=output(spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Pellet','max(wtd)'])
pellet_P2_bf1_min_wtd=output(spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Pellet','min(wtd)'])
lump_P2_bf1=output(spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Lump','Actual'])
lump_P2_bf1_max_wtd=output(spl_input_P2_bf1.loc[spl_input_P2_bf1['Parameter']=='Lump','max(wtd)'])

hot_metal_prodction_P2_bf1=output(Kg_by_Thm_P2_bf1)


# In[57]:


def output(self):
    op_list=list()
    for v, coefficient in lpSum(self).items():
        op_list.append(coefficient*v.varValue)
    op_total=lpSum(op_list).value()
    return op_total

#P2_bf2
sinter_P2_bf2=output(spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Sinter','Actual'])
sinter_P2_bf2_max_wtd=output(spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Sinter','max(wtd)'])
sinter_P2_bf2_min_wtd=output(spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Sinter','min(wtd)'])
pellet_P2_bf2=output(spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Pellet','Actual'])
pellet_P2_bf2_max_wtd=output(spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Pellet','max(wtd)'])
pellet_P2_bf2_min_wtd=output(spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Pellet','min(wtd)'])
lump_P2_bf2=output(spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Lump','Actual'])
lump_P2_bf2_max_wtd=output(spl_input_P2_bf2.loc[spl_input_P2_bf2['Parameter']=='Lump','max(wtd)'])

hot_metal_prodction_P2_bf2=output(Kg_by_Thm_P2_bf2)


# In[58]:


spl_output_dict={'BF1':[sinter_P2_bf1,pellet_P2_bf1,lump_P2_bf1,hot_metal_prodction_P2_bf1]}
spl_output_df=pd.DataFrame(data=spl_output_dict,index=['Sinter','Pellet','Lump','Hot Metal Production']).round(1)

#spl_output_df['Max(wtd) P1']=[sinter_P1_max_wtd,pellet_P1_max_wtd,lump_P1_max_wtd,0,0,0]
#spl_output_df['Max(wtd) BF2']=[sinter_P2_bf1_max_wtd,pellet_P2_bf1_max_wtd,lump_P2_bf1_max_wtd,0,0,0]
spl_output_df['% BF1']=spl_output_df['BF1']/(sinter_P2_bf1+pellet_P2_bf1+lump_P2_bf1)*100
spl_output_df=spl_output_df.round(1)
spl_output_df


# In[59]:


spl_output_dict={'BF2':[sinter_P2_bf2,pellet_P2_bf2,lump_P2_bf2,hot_metal_prodction_P2_bf2]}
spl_output_df=pd.DataFrame(data=spl_output_dict,index=['Sinter','Pellet','Lump','Hot Metal Production']).round(1)

#spl_output_df['Max(wtd) P1']=[sinter_P1_max_wtd,pellet_P1_max_wtd,lump_P1_max_wtd,0,0,0]
#spl_output_df['Max(wtd) BF2']=[sinter_P2_bf2_max_wtd,pellet_P2_bf2_max_wtd,lump_P2_bf2_max_wtd,0,0,0]
spl_output_df['% BF2']=spl_output_df['BF2']/(sinter_P2_bf2+pellet_P2_bf2+lump_P2_bf2)*100
spl_output_df=spl_output_df.round(1)
spl_output_df


# In[59]:


inventory_bmo


# In[60]:


bmo_materials

