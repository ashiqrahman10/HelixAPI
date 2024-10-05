from .doctor import doctor_router
from .patient import patient_router
from .lab import lab_router
from .system import system_router

__all__ = ["doctor_router", "patient_router", "lab_router", "system_router"]