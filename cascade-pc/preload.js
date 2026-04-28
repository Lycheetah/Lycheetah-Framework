const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('cascade', {
  pyramids: {
    list: () => ipcRenderer.invoke('pyramids:list'),
    create: (data) => ipcRenderer.invoke('pyramids:create', data),
    delete: (id) => ipcRenderer.invoke('pyramids:delete', id),
    setDisplayMode: (data) => ipcRenderer.invoke('pyramids:setDisplayMode', data),
  },
  files: {
    list: (pyramidId) => ipcRenderer.invoke('files:list', pyramidId),
    create: (data) => ipcRenderer.invoke('files:create', data),
    delete: (id) => ipcRenderer.invoke('files:delete', id),
    updateScore: (data) => ipcRenderer.invoke('files:updateScore', data),
    openDialog: () => ipcRenderer.invoke('files:openDialog'),
  },
  blocks: {
    list: (fileId) => ipcRenderer.invoke('blocks:list', fileId),
    create: (data) => ipcRenderer.invoke('blocks:create', data),
    delete: (id) => ipcRenderer.invoke('blocks:delete', id),
    updateScore: (data) => ipcRenderer.invoke('blocks:updateScore', data),
    setFrameworkRefs: (data) => ipcRenderer.invoke('blocks:setFrameworkRefs', data),
    updateNotes: (data) => ipcRenderer.invoke('blocks:updateNotes', data),
    duplicate: (id) => ipcRenderer.invoke('blocks:duplicate', id),
    appendHistory: (data) => ipcRenderer.invoke('blocks:appendHistory', data),
    saveVersion: (data) => ipcRenderer.invoke('blocks:saveVersion', data),
    getVersions: (id) => ipcRenderer.invoke('blocks:getVersions', id),
    pin: (data) => ipcRenderer.invoke('blocks:pin', data),
    setTags: (data) => ipcRenderer.invoke('blocks:setTags', data),
    updatePosition: (data) => ipcRenderer.invoke('blocks:updatePosition', data),
  },
  onion: {
    list: (blockId) => ipcRenderer.invoke('onion:list', blockId),
    updateFramework: (data) => ipcRenderer.invoke('onion:updateFramework', data),
    updateSovereign: (data) => ipcRenderer.invoke('onion:updateSovereign', data),
    update: (data) => ipcRenderer.invoke('onion:update', data),
  },
  experiments: {
    list: () => ipcRenderer.invoke('experiments:list'),
    create: (data) => ipcRenderer.invoke('experiments:create', data),
    saveResult: (data) => ipcRenderer.invoke('experiments:saveResult', data),
  },
  export: {
    save: (data) => ipcRenderer.invoke('export:save', data),
    fullDump: () => ipcRenderer.invoke('export:fullDump'),
  },
  audit: {
    log: (data) => ipcRenderer.invoke('audit:log', data),
    get: () => ipcRenderer.invoke('audit:get'),
  },
  api: {
    status: () => ipcRenderer.invoke('api:status'),
    start:  () => ipcRenderer.invoke('api:start'),
    stop:   () => ipcRenderer.invoke('api:stop'),
  },
})

