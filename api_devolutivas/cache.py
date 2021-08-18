#simple in-memory caching class

class Cache:
    
    def __init__(self):
        
        self.cache_dict = {}
    
    def get(self, search_data, offset):
        
        for tipo_obj, id_obj in search_data.items():
            dici_tipo = self.cache_dict.get(tipo_obj,{})
            dici_objeto = dici_tipo.get(id_obj,{})
            
            return dici_objeto.get(offset)

    def add(self, result_busca, search_data, offset):
        
        for tipo_obj, id_obj in search_data.items():
            if tipo_obj not in self.cache_dict:
                self.cache_dict[tipo_obj] = {}
            dici_tipo = self.cache_dict[tipo_obj]
            if id_obj not in dici_tipo:
                dici_tipo[id_obj] = {}    
            dici_objeto = dici_tipo[id_obj]
            
            if offset not in dici_objeto:
                dici_objeto[offset] = result_busca