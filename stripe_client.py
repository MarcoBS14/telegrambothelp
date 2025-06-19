# stripe_client.py

import os
import stripe
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Buscar el customer_id a partir del correo registrado en Stripe
def buscar_customer_id_por_email(email: str):
    try:
        clientes = stripe.Customer.list(email=email).data
        if clientes:
            return clientes[0].id
        else:
            print("❌ No se encontró el cliente en Stripe para ese correo.")
            return None
    except Exception as e:
        print(f"❌ Error buscando customer_id: {e}")
        return None

# Cancelar suscripción activa del cliente (inmediata y sin prorrateo)
def cancelar_suscripcion_por_customer_id(customer_id: str):
    try:
        suscripciones = stripe.Subscription.list(customer=customer_id, status='active').data
        if not suscripciones:
            print("❌ No hay suscripciones activas para este cliente.")
            return False

        subscription_id = suscripciones[0].id

        # Cancelación inmediata sin prorrateo ni cargos extra
        stripe.Subscription.delete(
            subscription_id,
            invoice_now=True,
            prorate=False
        )

        print(f"✅ Suscripción cancelada inmediatamente: {subscription_id}")
        return True

    except Exception as e:
        print(f"❌ Error cancelando suscripción: {e}")
        return False