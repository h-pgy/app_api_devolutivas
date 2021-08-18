#project-specific exceptions

class ResultadoVazio(ValueError):
    '''Raised para mostrar quando acabaram os resultados de uma busca'''

class MuitasRequisicoes(ValueError):
    '''Raised para mostrar quando foram feitas requisicoes demais'''