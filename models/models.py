from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import EmailStr, validator
from datetime import date
from sqlalchemy import Column, Boolean, Enum
import enum

# ENUMS PERSONALIZADOS, los cuales dan cumplimiento a cierta restricciones que son necesarias para el sistema

class TipoBateria(str, enum.Enum):    #Enum que nos permite establecer que tipos de baterías se manejan en el sistema
    LITIO_ION = "Litio-ion"
    PLOMO_ACIDO = "Plomo-ácido"
    NIMH = "NiMH"
    SOLIDA = "Sólida"


class EstadoBateria(str, enum.Enum):   #Enum que nos permite establecer estados para las baterias que se encuerntran registradas dentro del sistema
    DISPONIBLE = "Disponible"
    EN_USO = "En uso"
    EN_MANTENIMIENTO = "En mantenimiento"


class RolUsuario(str, enum.Enum):  #Enum que nos permite establecer roles que puede tener un usuario en la página
    ADMIN = "admin"
    TECNICO = "tecnico"
    CLIENTE = "cliente"


class MarcaVehiculo(str, enum.Enum):     #Enum que nos permite establecer unas determinadas marcas dentro del taller
    TESLA = "Tesla"
    NISSAN = "Nissan"
    BMW = "BMW"
    RENAULT = "Renault"
    CHEVROLET = "Chevrolet"

class EstadoVehiculo(str, enum.Enum):          #Enum que nos permite establcer un estado para el vehículo
    DISPONIBLE = "Disponible"
    EN_TALLER = "En taller"
    EN_MANTENIMIENTO = "En mantenimiento"


class EstadoCita(str, enum.Enum):              #Enum que nos permite establecer un estado para las citas
    PENDIENTE = "Pendiente"
    EN_PROGRESO = "En progreso"
    COMPLETADA = "Completada"

# MODELOS

class Vehiculo(SQLModel, table=True):           #Creación del modelo vehículo
    id: Optional[int] = Field(default=None, primary_key=True)#Creación de campo
    marca: MarcaVehiculo#Creación de campo
    modelo: str#Creación de campo
    año: int#Creación de campo
    imagen_url: Optional[str] = Field(default=None, description="URL de la imagen del vehículo")#Creación de campo
    estado: EstadoVehiculo = Field(
        sa_column=Column(Enum(EstadoVehiculo), default=EstadoVehiculo.DISPONIBLE)#Creación de campo
    )
    eliminado: bool = Field(default=False, sa_column=Column(Boolean, default=False))#Creación de campo

    bateria: Optional["Bateria"] = Relationship(
        back_populates="vehiculo",
        sa_relationship_kwargs={"uselist": False}
    )
    citas: List["Cita"] = Relationship(back_populates="vehiculo")    #Creación de la relación entre vehículo y cita


class Bateria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)#Creación de llave primaria
    codigo: str = Field(index=True, unique=True, nullable=False)#Creación de campo
    tipo: TipoBateria = Field(sa_column=Column(Enum(TipoBateria), nullable=False))#Creación de campo
    capacidad_kWh: float#Creación de campo
    estado_salud: float = Field(gt=0, le=100)#Creación de restricciones
    ciclos_carga: Optional[int] = Field(default=0, ge=0)#Creación de restricciones
    temperatura_operacion: Optional[float] = Field(default=None)#Creación de campo
    estado: EstadoBateria = Field(
        sa_column=Column(Enum(EstadoBateria), default=EstadoBateria.DISPONIBLE)#Creación de campo
    )
    vehiculo_id: Optional[int] = Field(default=None, foreign_key="vehiculo.id")#Creación de campo
    eliminado: bool = Field(default=False)#Creación de campo

    vehiculo: Optional[Vehiculo] = Relationship(back_populates="bateria")#Creación de la relación entre vehículo y Bateria

    @validator("estado_salud")
    def validar_estado_salud(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("El estado de salud debe estar entre 0 y 100.")#Creación de restricciones
        return v


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)#Creación de restricciones
    nombre: str = Field(index=True, min_length=2, max_length=50)#Creación de restricciones
    apellido: str = Field(index=True, min_length=2, max_length=50)#Creación de restricciones
    email: EmailStr = Field(unique=True, index=True)#Creación de restricciones
    telefono: Optional[str] = Field(default=None)#Creación de campo
    direccion: Optional[str] = Field(default=None)#Creación de campo
    contraseña: str = Field(min_length=6)#Creación de restricciones
    rol: RolUsuario = Field(sa_column=Column(Enum(RolUsuario), nullable=False))#Creación de campo
    fecha_registro: date = Field(default_factory=date.today)#Creación de campo
    activo: bool = Field(default=True, sa_column=Column(Boolean, default=True))#Creación de campo
    eliminado: bool = Field(default=False, sa_column=Column(Boolean, default=False))#Creación de campo

    # Relaciones con Cita
    citas_cliente: List["Cita"] = Relationship(
        back_populates="cliente",
        sa_relationship_kwargs={"foreign_keys": "[Cita.cliente_id]"}#Creación de la relación entre cliente y cita
    )
    citas_tecnico: List["Cita"] = Relationship(
        back_populates="tecnico",
        sa_relationship_kwargs={"foreign_keys": "[Cita.tecnico_id]"}#Creación de la relación entre tecnico y cita
    )

    @validator("contraseña")
    def validar_contraseña(cls, v):
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        return v

    @validator("nombre")
    def validar_nombre(cls, v):
        if not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError("El nombre solo puede contener letras y espacios.")
        return v


class Cita(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="usuario.id")
    tecnico_id: int = Field(foreign_key="usuario.id")
    vehiculo_id: int = Field(foreign_key="vehiculo.id")
    fecha: date
    hora: str
    costo: float
    estado: EstadoCita = Field(sa_column=Column(Enum(EstadoCita), default=EstadoCita.PENDIENTE))

    cliente: Optional[Usuario] = Relationship(
        back_populates="citas_cliente",
        sa_relationship_kwargs={"foreign_keys": "[Cita.cliente_id]"}#Creación de la relación entre cliente y cita
    )
    tecnico: Optional[Usuario] = Relationship(
        back_populates="citas_tecnico",
        sa_relationship_kwargs={"foreign_keys": "[Cita.tecnico_id]"}#Creación de la relación entre tecnico y cita
    )
    vehiculo: Optional[Vehiculo] = Relationship(back_populates="citas")