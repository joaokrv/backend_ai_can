from enum import Enum


class Sexo(str, Enum):
    MASCULINO = "M"
    FEMININO = "F"
    OUTRO = "O"
    PREFIRO_NAO_DIZER = "N"


class DiaSemana(str, Enum):
    SEGUNDA = "segunda"
    TERCA = "terca"
    QUARTA = "quarta"
    QUINTA = "quinta"
    SEXTA = "sexta"
    SABADO = "sabado"
    DOMINGO = "domingo"


class RestricaoAlimentar(str, Enum):
    LACTOSE = "lactose"
    GLUTEN = "gluten"
    AMENDOIM = "amendoim"
    FRUTOS_DO_MAR = "frutos_do_mar"
    OVOS = "ovos"
    SOJA = "soja"
    VEGETARIANO = "vegetariano"
    VEGANO = "vegano"
    SEM_ACUCAR = "sem_acucar"
    LOW_CARB = "low_carb"
    CETOGENICA = "cetogenica"
    PALEO = "paleo"


class NivelExperiencia(str, Enum):
    INICIANTE = "iniciante"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"


class ObjetivoTreino(str, Enum):
    PERDER_PESO = "perder"
    GANHAR_PESO = "ganhar"
    HIPERTROFIA = "hipertrofia"
    DEFINICAO = "definicao"


class LocalTreino(str, Enum):
    ACADEMIA = "academia"
    CASA = "casa"
    AR_LIVRE = "arLivre"


class TipoFeedback(str, Enum):
    EXERCICIO = "exercicio"
    REFEICAO = "refeicao"


class StatusPlano(str, Enum):
    ATIVO = "ativo"
    ARQUIVADO = "arquivado"


OBJETIVO_LABELS = {
    ObjetivoTreino.PERDER_PESO: "Perder peso",
    ObjetivoTreino.GANHAR_PESO: "Ganhar peso",
    ObjetivoTreino.HIPERTROFIA: "Hipertrofia muscular",
    ObjetivoTreino.DEFINICAO: "Definicao muscular",
}

LOCAL_LABELS = {
    LocalTreino.ACADEMIA: "Academia",
    LocalTreino.CASA: "Em casa",
    LocalTreino.AR_LIVRE: "Ao ar livre",
}
