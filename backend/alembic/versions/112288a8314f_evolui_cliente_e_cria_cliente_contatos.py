"""evolui cliente e cria cliente_contatos

Revision ID: 112288a8314f
Revises: 9e90f77d4d8c
Create Date: 2026-02-25 11:10:08.467275

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "112288a8314f"
down_revision: Union[str, None] = "9e90f77d4d8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- clientes: dados cadastrais completos + soft delete ---
    op.add_column("clientes", sa.Column("cnpj", sa.String(length=20), nullable=True))
    op.add_column("clientes", sa.Column("ie", sa.String(length=30), nullable=True))

    op.add_column(
        "clientes",
        sa.Column("endereco_logradouro", sa.String(length=180), nullable=True),
    )
    op.add_column(
        "clientes",
        sa.Column("endereco_numero", sa.String(length=20), nullable=True),
    )

    op.add_column("clientes", sa.Column("bairro", sa.String(length=80), nullable=True))
    op.add_column("clientes", sa.Column("cidade", sa.String(length=80), nullable=True))
    op.add_column("clientes", sa.Column("estado", sa.String(length=2), nullable=True))
    op.add_column("clientes", sa.Column("cep", sa.String(length=12), nullable=True))

    op.add_column("clientes", sa.Column("observacoes", sa.Text(), nullable=True))

    # Soft delete
    op.add_column(
        "clientes",
        sa.Column(
            "ativo",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )

    # Índice UNIQUE para CNPJ (permite múltiplos NULLs; impede duplicados não-nulos)
    op.create_index(op.f("ux_clientes_cnpj"), "clientes", ["cnpj"], unique=True)

    # --- cliente_contatos: 1 cliente -> N contatos ---
    op.create_table(
        "cliente_contatos",
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("nome_contato", sa.String(length=120), nullable=False),
        sa.Column("cargo", sa.String(length=120), nullable=True),
        sa.Column("email", sa.String(length=180), nullable=True),
        sa.Column("telefone", sa.String(length=40), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column(
            "ativo",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_cliente_contatos_cliente_id"),
        "cliente_contatos",
        ["cliente_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cliente_contatos_email"),
        "cliente_contatos",
        ["email"],
        unique=False,
    )


def downgrade() -> None:
    # --- desfaz cliente_contatos ---
    op.drop_index(op.f("ix_cliente_contatos_email"), table_name="cliente_contatos")
    op.drop_index(op.f("ix_cliente_contatos_cliente_id"), table_name="cliente_contatos")
    op.drop_table("cliente_contatos")

    # --- desfaz clientes ---
    op.drop_index(op.f("ux_clientes_cnpj"), table_name="clientes")
    op.drop_column("clientes", "ativo")
    op.drop_column("clientes", "observacoes")
    op.drop_column("clientes", "cep")
    op.drop_column("clientes", "estado")
    op.drop_column("clientes", "cidade")
    op.drop_column("clientes", "bairro")
    op.drop_column("clientes", "endereco_numero")
    op.drop_column("clientes", "endereco_logradouro")
    op.drop_column("clientes", "ie")
    op.drop_column("clientes", "cnpj")