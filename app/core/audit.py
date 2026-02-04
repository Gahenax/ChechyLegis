from sqlalchemy import event
from sqlalchemy.orm import Session
from ..models import Proceso, AuditLog
from .context import get_current_user_name
import json

def register_audit_listeners():
    @event.listens_for(Proceso, 'after_insert')
    def receive_after_insert(mapper, connection, target):
        usuario = get_current_user_name()
        # Capturamos el estado inicial
        data = {c.name: getattr(target, c.name) for c in target.__table__.columns}
        
        # Insertar log usando una conexión directa para no interferir con la sesión actual
        connection.execute(
            AuditLog.__table__.insert().values(
                usuario=usuario,
                accion="CREATE",
                entidad="PROCESO",
                entidad_id=target.id,
                valor_nuevo=json.dumps(data, default=str)
            )
        )

    @event.listens_for(Proceso, 'after_update')
    def receive_after_update(mapper, connection, target):
        usuario = get_current_user_name()
        state = target.__mapper__.attrs
        
        for attr in state:
            hist = attr.history
            if hist.has_changes():
                col_name = attr.key
                old_val = hist.deleted[0] if hist.deleted else None
                new_val = hist.added[0] if hist.added else getattr(target, col_name)
                
                if old_val != new_val:
                    connection.execute(
                        AuditLog.__table__.insert().values(
                            usuario=usuario,
                            accion="UPDATE",
                            entidad="PROCESO",
                            entidad_id=target.id,
                            campo_modificado=col_name,
                            valor_anterior=str(old_val),
                            valor_nuevo=str(new_val)
                        )
                    )
