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

# 🔓 Permitir conexión desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambia esto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📌 Modelo base
class TicketBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    descripcion: str = Field(..., min_length=5)
    estado: str = Field(default="abierto")
    tecnico: Optional[str] = None

# 📌 Modelo para crear
class TicketCreate(TicketBase):
    pass

# 📌 Modelo para actualizar (parcial)
class TicketUpdate(BaseModel):
    titulo: Optional[str]
    descripcion: Optional[str]
    estado: Optional[str]
    tecnico: Optional[str]

# 📌 Modelo de respuesta
class Ticket(TicketBase):
    id: int

# 🗄️ Base de datos simulada
tickets: List[Ticket] = []
contador_id = 1

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
    name="index.html",
    context={"request": request}
)

# ✅ Crear ticket
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


# ✅ Obtener todos
@app.get("/tickets/", response_model=List[Ticket], tags=["Tickets"])
def obtener_tickets():
    return tickets


# ✅ Obtener por ID
@app.get("/tickets/{ticket_id}", response_model=Ticket, tags=["Tickets"])
def obtener_ticket(ticket_id: int):
    for t in tickets:
        if t.id == ticket_id:
            return t
    raise HTTPException(status_code=404, detail="Ticket no encontrado")


# ✅ Actualizar ticket (parcial)
@app.patch("/tickets/{ticket_id}", response_model=Ticket, tags=["Tickets"])
def actualizar_ticket(ticket_id: int, ticket: TicketUpdate):
    for i, t in enumerate(tickets):
        if t.id == ticket_id:

            datos_actualizados = ticket.dict(exclude_unset=True)

            ticket_actualizado = t.copy(update=datos_actualizados)
            tickets[i] = ticket_actualizado

            return ticket_actualizado

    raise HTTPException(status_code=404, detail="Ticket no encontrado")


# ✅ Eliminar ticket
@app.delete("/tickets/{ticket_id}", tags=["Tickets"])
def eliminar_ticket(ticket_id: int):
    for i, t in enumerate(tickets):
        if t.id == ticket_id:
            eliminado = tickets.pop(i)
            return {"mensaje": "Ticket eliminado", "ticket": eliminado}

    raise HTTPException(status_code=404, detail="Ticket no encontrado")