"""Define exceções personalizadas do projeto."""


class ErroDadosError(RuntimeError):
    """Erro disparado quando arquivos de dados essenciais não podem ser carregados."""


__all__ = ["ErroDadosError"]
