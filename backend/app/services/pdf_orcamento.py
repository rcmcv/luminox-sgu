"""
Wrapper de compatibilidade.

Mantém o import antigo funcionando:
  from app.services.pdf_orcamento import generate_orcamento_pdf

Agora a implementação real mora em:
  app.services.pdf.service
"""

from app.services.pdf.service import generate_orcamento_pdf, escolher_layout_cliente

__all__ = ["generate_orcamento_pdf", "escolher_layout_cliente"]
