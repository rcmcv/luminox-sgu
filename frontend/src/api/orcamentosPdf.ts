import api from "./client";

/**
 * Baixa o PDF do orçamento (backend retorna application/pdf).
 * Retorna um Blob que pode ser salvo/aberto no browser.
 */
export async function downloadOrcamentoPdf(orcamentoId: number): Promise<Blob> {
  const response = await api.get(`/orcamentos/${orcamentoId}/pdf`, {
    responseType: "blob", // essencial para PDF
  });

  return response.data as Blob;
}
