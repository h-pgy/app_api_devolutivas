#utilidades para fazer a regionalizacao
import geopandas as gpd


class RegiaoCounter:

    def __init__(self, remover_n_regional=False, return_ids=False):

        self.remover_n_regional = remover_n_regional
        self.return_ids = return_ids

    def count_subprefeitura_data(self, data, cathegory_name, return_ids=False):

        parsed_data = {}
        
        for contrib in data[cathegory_name]:
            for sug in contrib['sugestoes']:
                if not return_ids:
                    subs = sug['subprefeitura']['nome']
                else:
                    subs = sug['subprefeitura']['id']
                if subs not in parsed_data:
                    parsed_data[subs] = 0

                parsed_data[subs]+=1
        
        return parsed_data

    def percentual_com_nao_regionalizado(self, parsed_data):

        total = sum(parsed_data.values())
                
        return {subs:round((valor/total)*100,2) 
                for subs, valor in parsed_data.items()}

    def percentual_apenas_subs(self, parsed_data):

        n_regional = 'Sugestão não regionalizada'
        total = sum([val for chave, val in parsed_data.items()
                    if chave != n_regional])
        return {subs:round((valor/total)*100,2) 
            for subs, valor in parsed_data.items()
                if subs != n_regional}

    def distribuicao_regional(self, data, cathegory_name, remover_n_regional=False, return_ids=False):

        parsed_data = self.count_subprefeitura_data(data, cathegory_name, return_ids)

        if not remover_n_regional:
            return self.percentual_com_nao_regionalizado(parsed_data)
        else:
            return self.percentual_apenas_subs(parsed_data)

    def __call__(self, data, cathegory_name):

        dados =  self.distribuicao_regional(data, cathegory_name, self.remover_n_regional, 
                                            self.return_ids)
        return dados
    

class Regionalizador:

    def __init__(self, shp_path):
        
        self.shp_path = shp_path
        self.contabilizar_subs = RegiaoCounter(remover_n_regional=True,
                                                return_ids=True)

        self.geodf_subs = self.abrir_geodf(shp_path)

    def projecao_lat_long(self, geodf):
    
        geodf.set_crs(epsg='31983', inplace=True)
        geodf.to_crs(epsg=4326,inplace=True)

    def abrir_geodf(self, file_path=None, arrumar_projecao=True):

        if file_path is None:
            file_path = self.file_path

        geodf = gpd.read_file(file_path)

        if arrumar_projecao:
            self.projecao_lat_long(geodf)

        return geodf

    def coluna_percentual_regional(self, geodf, dados_regionais, col_name = "Percentual"):

        geodf[col_name] = geodf['sp_id'].apply(lambda x: dados_regionais.get(x, 0))
    
    def geodf_distrib_regional(self, geodf, api_data, cathegory_name, col_name="Percentual"):
        
        geodf = geodf.copy()

        dados_regionais = self.contabilizar_subs(api_data, cathegory_name)
        self.coluna_percentual_regional(geodf, dados_regionais, col_name)

        return geodf

    def __call__(self, api_data, cathegory_name, col_name="Percentual"):
        
        geodf = self.geodf_distrib_regional(self.geodf_subs,
                                            api_data,
                                            cathegory_name,
                                            col_name)

        return geodf