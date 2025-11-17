from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import get_settings
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.clientes import router as clientes_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.fornecedores import router as fornecedores_router
from app.api.v1.endpoints.tipos_servico import router as tipos_servico_router
from app.api.v1.endpoints.unidades_medida import router as unidades_medida_router
from app.api.v1.endpoints.materiais import router as materiais_router
from app.api.v1.endpoints.maquinas import router as maquinas_router
from app.api.v1.endpoints.contratos import router as contratos_router
from app.api.v1.endpoints.contrato_hh_precos import router as contrato_hh_precos_router
from app.api.v1.endpoints.contrato_material_precos import router as contrato_material_precos_router
from app.api.v1.endpoints.contratos_precos import router as contratos_precos_router
from app.api.v1.endpoints.orcamentos import router as orcamentos_router
from app.api.v1.endpoints.orcamento_itens import router as orcamento_itens_router

from app.core.error_handlers import register_error_handlers
from app.core.middlewares import RequestIDMiddleware

settings = get_settings()

def create_app() -> FastAPI:
    """
    Fábrica da aplicação para facilitar testes e futuras configurações.
    Agora usa Settings (Pydantic) para metadados e CORS.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Backend inicial do sistema de gestão de usinagem."
    )

    # CORS: em dev liberado; em prod restrito (defina CORS_ORIGINS no ambiente)
    app.add_middleware(RequestIDMiddleware)  # <-- Request ID
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Handlers globais
    register_error_handlers(app)             # <-- registra handlers

    # Rotas v1
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])
    app.include_router(auth_router, prefix="/api/v1", tags=["Auth & Users"])
    app.include_router(clientes_router, prefix="/api/v1", tags=["Clientes"])
    app.include_router(fornecedores_router, prefix="/api/v1", tags=["Fornecedores"])
    app.include_router(tipos_servico_router, prefix="/api/v1", tags=["Tipos de Serviço"])
    app.include_router(unidades_medida_router, prefix="/api/v1", tags=["Unidades de Medida"])
    app.include_router(materiais_router, prefix="/api/v1", tags=["Materiais"])
    app.include_router(maquinas_router, prefix="/api/v1", tags=["Maquinas"])
    app.include_router(contratos_router, prefix="/api/v1", tags=["Contratos"])
    app.include_router(contrato_hh_precos_router, prefix="/api/v1", tags=["Contrato — HH por Máquina"])
    app.include_router(contrato_material_precos_router, prefix="/api/v1", tags=["Contrato — Materiais"])
    app.include_router(contratos_precos_router, prefix="/api/v1", tags=["Contratos — Preços (resolver)"])
    app.include_router(orcamentos_router, prefix="/api/v1", tags=["Orçamentos"])
    app.include_router(orcamento_itens_router, prefix="/api/v1", tags=["Orçamentos - Itens"])
    
    @app.get("/", tags=["Root"])
    def root():
        """
        Endpoint raiz para validar se a API está no ar e ver o ambiente ativo.
        Não expõe segredos.
        """
        return {
            "message": "API de Usinagem no ar. Veja /api/v1/health",
            "env": settings.ENV,
            "version": settings.VERSION
        }

    return app

app = create_app()
