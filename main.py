from tempfile import template

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")



app = FastAPI(
    title="Help Desk API",
    description="API para gestión de incidencias TI",
    version="2.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TicketBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    descripcion: str = Field(..., min_length=5)
    estado: str = Field(default="abierto")
    tecnico: Optional[str] = None


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    titulo: Optional[str]
    descripcion: Optional[str]
    estado: Optional[str]
    tecnico: Optional[str]


class Ticket(TicketBase):
    id: int


tickets: List[Ticket] = []
contador_id = 1



@app.post("/tickets/", response_model=Ticket, tags=["Tickets"])
def crear_ticket(ticket: TicketCreate):
    global contador_id

    nuevo_ticket = Ticket(
        id=contador_id,
        **ticket.dict()
    )

    contador_id += 1
    tickets.append(nuevo_ticket)

    return nuevo_ticket



@app.get("/tickets/", response_model=List[Ticket], tags=["Tickets"])
def obtener_tickets():
    return tickets



@app.get("/tickets/{ticket_id}", response_model=Ticket, tags=["Tickets"])
def obtener_ticket(ticket_id: int):
    for t in tickets:
        if t.id == ticket_id:
            return t
    raise HTTPException(status_code=404, detail="Ticket no encontrado")



@app.patch("/tickets/{ticket_id}", response_model=Ticket, tags=["Tickets"])
def actualizar_ticket(ticket_id: int, ticket: TicketUpdate):
    for i, t in enumerate(tickets):
        if t.id == ticket_id:

            datos_actualizados = ticket.dict(exclude_unset=True)

            ticket_actualizado = t.copy(update=datos_actualizados)
            tickets[i] = ticket_actualizado

            return ticket_actualizado

    raise HTTPException(status_code=404, detail="Ticket no encontrado")



@app.delete("/tickets/{ticket_id}", tags=["Tickets"])
def eliminar_ticket(ticket_id: int):
    for i, t in enumerate(tickets):
        if t.id == ticket_id:
            eliminado = tickets.pop(i)
            return {"mensaje": "Ticket eliminado", "ticket": eliminado}

    raise HTTPException(status_code=404, detail="Ticket no encontrado")

@app.get("/")
def interfaz():
    return FileResponse("templates/index.html")

