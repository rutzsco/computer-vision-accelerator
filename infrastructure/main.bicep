// Configurable input parameters
@description('The environment suffix to append to resource names.')
param environmentSuffix string = 'ci'

@description('The environment prefix to append to resource names.')
param environmentName string = 'computer-vision'

@description('The environment prefix to append to resource names.')
param environmentNameShort string = 'computervision'

@description('The admin password for SQL Server.')
@secure()
param sqlAdministratorLoginPassword string

// Resource names
var acrResourceName = '${environmentName}acr${environmentSuffix}'
var saResourceName = '${environmentNameShort}sa${environmentSuffix}'
var sqlServerResourceName = '${environmentNameShort}sql-${environmentSuffix}'

// ACR
module azureContainerRegistry 'acr.bicep' = {
  name: 'azureContainerRegistryDeploy'
  params: {
    acrName: acrResourceName
  }
}

// IotHub
module iothub 'iot-hub.bicep' = {
  name: 'iothub'
  params: {
    environmentName: environmentName
    environmentSuffix: environmentSuffix
  }
}

// Storage Account
module sa 'storage-account.bicep' = {
  name: 'sa'
  params: {
    storageAccountName: saResourceName
  }
}

// SQL
module sql 'sql-database.bicep' = {
  name: 'sql'
  params: {
    serverName: sqlServerResourceName
    sqlDBName: 'SampleDB'
    administratorLogin: 'developer'
    administratorLoginPassword: sqlAdministratorLoginPassword
  }
}

output acrName string = azureContainerRegistry.outputs.acrName
output acrLoginServer string = azureContainerRegistry.outputs.acrLoginServer
