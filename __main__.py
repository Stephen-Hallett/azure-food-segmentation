import pulumi
import pulumi_azure_native as azure_native  # Import the Azure Native provider with updated resource types
import os
from dotenv import load_dotenv; load_dotenv()
import json

global_name = os.getenv("PROJECT")

# Create a resource group for all our resources
resource_group = azure_native.resources.ResourceGroup(global_name+"_resource")

# Now let's create a storage account required by the Azure ML workspace
account = azure_native.storage.StorageAccount(
    global_name+"sa",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    sku=azure_native.storage.SkuArgs(
        name=azure_native.storage.SkuName.STANDARD_LRS,
    ),
    kind=azure_native.storage.Kind.STORAGE_V2,
)

app_insights = azure_native.insights.Component(global_name + "appinsights",
                                               resource_group_name=resource_group.name,
                                               location=resource_group.location,
                                               kind="other",
                                               application_type="other",
                                               ingestion_mode="ApplicationInsights")

key_vault = azure_native.keyvault.Vault(global_name+"vault",
                           resource_group_name=resource_group.name,
                           properties=azure_native.keyvault.VaultPropertiesArgs(
                               tenant_id=os.getenv("TENANT_ID"),
                               sku=azure_native.keyvault.SkuArgs(family="A",
                                                                 name="Standard"),
                               access_policies=[],
                           ),
                           location=resource_group.location)

# # Create an Azure Machine Learning workspace
ml_workspace = azure_native.machinelearningservices.Workspace(
    global_name+"-ml-workspace",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    sku=azure_native.machinelearningservices.SkuArgs(
        name="Basic", 
    ),
    identity=azure_native.machinelearningservices.IdentityArgs(
        type="SystemAssigned",  # Other options include 'UserAssigned' or 'None'
    ),
    storage_account=account.id,
    application_insights=app_insights.id,
    key_vault=key_vault,
    description=global_name+" machine learning workspace",
)

primary_storage_key = pulumi.Output.all(resource_group.name, account.name).apply(
    lambda args: azure_native.storage.list_storage_account_keys(resource_group_name=args[0],
                                                               account_name=args[1]).keys[0].value)

# Export the resulting configuration
pulumi.export("primary_storage_key", primary_storage_key)
pulumi.export('resource_group',resource_group.name)
pulumi.export('storage',account.name)
pulumi.export('app_insights',app_insights.name)
pulumi.export('keyvault',key_vault.name)
pulumi.export('ml_workspace',ml_workspace.name)
