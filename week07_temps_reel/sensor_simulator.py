"""Simulateur de capteurs : envoie des mesures JSON vers un Eventstream (source Custom Endpoint).

Variables d'environnement :
  EVENTSTREAM_CONN_STR  chaîne de connexion Event Hubs-compatible fournie par l'Eventstream
  EVENTHUB_NAME         nom de l'entité
Dépendance : pip install azure-eventhub
"""
import json, os, random, time
from datetime import datetime, timezone
from azure.eventhub import EventHubProducerClient, EventData

SITES = ["parc-eolien-nord", "centrale-solaire-sud", "poste-source-est"]

def measure(site):
    base = {"parc-eolien-nord": 120, "centrale-solaire-sud": 80, "poste-source-est": 200}[site]
    value = max(0, random.gauss(base, base * 0.1))
    if random.random() < 0.02:       # 2 % d'anomalies pour tester les alertes
        value *= 3
    return {"site": site, "power_mw": round(value, 2),
            "ts": datetime.now(timezone.utc).isoformat()}

def main():
    producer = EventHubProducerClient.from_connection_string(
        os.environ["EVENTSTREAM_CONN_STR"], eventhub_name=os.environ["EVENTHUB_NAME"])
    with producer:
        while True:
            batch = producer.create_batch()
            for s in SITES:
                batch.add(EventData(json.dumps(measure(s))))
            producer.send_batch(batch)
            time.sleep(2)

if __name__ == "__main__":
    main()
