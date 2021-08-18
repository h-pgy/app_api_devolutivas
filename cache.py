#simple in-memory caching class

class Cache:
    
    def __init__(self):
        
        self.cache_dict = {}
    
    def get(self, search_data, offset):
        
        for tipo_obj, id_obj in search_data.items():
            dici_tipo = self.cache_dict.get(tipo_obj,{})
            dici_objeto = dici_tipo.get(id_obj,{})
            
            return dici_objeto.get(offset)