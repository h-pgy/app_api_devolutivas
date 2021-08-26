#cliente API devolutivas
import random
import time
import requests
from .cache import Cache
from .exceptions import ResultadoVazio, MuitasRequisicoes

class ClientDevolutivas:
    
    root = 'https://devolutiva.pdm.prefeitura.sp.gov.br/api/v1/'
    limite_requisicoes=1000
    
    def __init__(self, cache = None, limite_linhas = 100):
        
        self.limite_linhas = limite_linhas
        
        self.categorias = self.get_types('categorias')
        self.eixos = self.get_types('eixos')
        self.secretarias = self.get_types('secretarias')
        self.subprefeituras = self.get_types('subprefeituras')
        
        self.cache = cache or Cache()
        
    def build_req_repr(self, r):
        
        body = getattr(r.request, 'body', b'')
        if body:
            body = body.decode('utf-8')
        else:
            body=''
                
        return r.url + body
                
    def check_statuses(self, r):
        
        req_repr = self.build_req_repr(r)
        if r.status_code == 204:
                raise ResultadoVazio(f'A busca para {req_repr} retornou vazio')
        elif r.status_code == 500:
            raise RuntimeError('Erro interno no servidor')
        elif r.status_code == 429:
            raise MuitasRequisicoes(f'Muitas requisicoes para a busca {req_repr}')
        elif r.status_code == 200:
            return r.json()
        else:
            raise RuntimeError(f'Comportamento inesperado para a busca: {req_repr}')
            
    def assert_tipos(self, tipo):
        
        tipos_aceitos = ('secretarias', 'subprefeituras',
                           'categorias', 'eixos')
        if tipo not in tipos_aceitos:
            raise ValueError(f'Os tipos disponíveis são {tipos_aceitos}')
            
    def get_types(self, tipo):
        
        self.assert_tipos(tipo)
        num_requisi=0
        while True:
            try:
                with requests.get(self.root+tipo) as r:
                    self.check_statuses(r)
                    dados = r.json()
                    return dados
            except MuitasRequisicoes as e:
                num_requisi+=1
                self.solve_too_many_reqs(num_requisi, e)
                return self.get_types(tipo)
            
        
    
    def find_obj_id(self, tipo_obj, nome_obj):
        
        valores = getattr(self, tipo_obj)
        try:
            if tipo_obj == 'secretarias':
                return [item['id'] for item in valores if 
                       item['sigla']==nome_obj][0]
            else:
                return [item['id'] for item in valores if 
                       item['nome']==nome_obj][0]
        except IndexError:
            raise ValueError(f'O valor {nome_obj} não existe para a coleção {tipo_obj}')
        
    def build_search_key(self, tipo_obj):
        
        chave_busca = f"id{tipo_obj.capitalize()}"
        if chave_busca.endswith('s'):
            chave_busca = chave_busca[:-1]
        
        return chave_busca

    
    def build_search_data(self, tipo_obj, nome_obj):
        
        self.assert_tipos(tipo_obj)
        
        chave_busca = self.build_search_key(tipo_obj)
        valor_busca = self.find_obj_id(tipo_obj, nome_obj)
        
        return {chave_busca : valor_busca}
    
    
    def post_pesquisar(self, search_data, offset):
        
        url = (self.root +
               f'contribuicoes/pesquisar?limit={self.limite_linhas}&offset={offset}')
                
        with requests.post(url, json=search_data,
                          headers = {"Content-Type": "application/json"}) as r:
            return self.check_statuses(r) 
    
    def pesquisar(self, tipo_obj, nome_obj, offset=0):
        
        self.assert_tipos(tipo_obj)
        
        search_data = self.build_search_data(tipo_obj, nome_obj)
        cache = self.cache.get(search_data, offset)
        if cache:
            print(f'Busca {search_data} cacheada')
            if cache=='FimDaBusca':
                raise ResultadoVazio(f'Busca {search_data} toda em cache')
            return cache
        
        else:
            try:
                data = self.post_pesquisar(search_data, offset)
                self.cache.add(data, search_data, offset)
                return data
            except ResultadoVazio as e:
                self.cache.add('FimDaBusca', search_data, offset)
                raise ResultadoVazio(e)
                
        
    def solve_too_many_reqs(self, num_requisi, e):
        
        if num_requisi<self.limite_requisicoes:
            time.sleep(random.randint(0,5))
        else:
            raise RuntimeError(f'Limite de retentativas excedido. {e}')
        
    def get_all_contribs_by_obj(self, tipo_obj, nome_obj):
        
        
        contribs = []
        
        offset = 0
        num_requisi = 0
        
        while True:
            try:
                data = self.pesquisar(tipo_obj, nome_obj, offset)
                num_requisi+=1
                if type(data) is list:
                    contribs.extend(data)
                else:
                    contribs.append(data)
                offset+=self.limite_linhas
            except ResultadoVazio as e:
                print(f'A busca para {tipo_obj}: {nome_obj} foi finalizada')
                print(e)
                break
            except MuitasRequisicoes as e:
                self.solve_too_many_reqs(num_requisi, e)
        
        return contribs
    
    def get_all_contribs_by_type(self, tipo_obj):
        
            
        all_data = {}
        for obj in getattr(self, tipo_obj):
            nome_obj = obj.get('nome') or obj.get('sigla')
            data = self.get_all_contribs_by_obj(tipo_obj,nome_obj)
            all_data[nome_obj]=data
        
        return all_data