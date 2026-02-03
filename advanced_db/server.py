# server.py - SAMO ZA POKRETANJE SERVERA
import os
import sys
from pathlib import Path

# Dodaj trenutni folder u Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Pokreće FastAPI server za Book Scraper Dashboard"""
    
    # ASCII art banner
    banner = """
    ╔═══════════════════════════════════════════════════╗
    ║      📚 ADVANCED BOOK SCRAPER DASHBOARD 🚀       ║
    ╚═══════════════════════════════════════════════════╝
    """
    print(banner)
    
    # Proveri da li postoji web/app.py
    if not (current_dir / "web" / "app.py").exists():
        print("❌ Greška: web/app.py ne postoji!")
        print("   Proveri da li si u root folderu projekta")
        return
    
    # Informacije za korisnika
    print("📍 Direktorijum:", current_dir)
    print("\n🌐 SERVER JE POKRENUT!")
    print("   └─ Dashboard:  http://localhost:8000")
    print("   └─ API Docs:   http://localhost:8000/docs")
    print("   └─ Health:     http://localhost:8000/health")
    print("   └─ System:     http://localhost:8000/api/v1/info")
    
    print("\n⚡ BRZI TEST:")
    print("   └─ Books API:  http://localhost:8000/api/books?limit=5")
    print("   └─ Stats:      http://localhost:8000/api/stats")
    
    print("\n🎮 KONTROLE:")
    print("   └─ Zaustavi:   Ctrl+C")
    print("   └─ Restart:    automatski pri promeni koda")
    
    print("\n" + "─" * 50)
    print("💡 Savet: Otvori http://localhost:8000 u browseru!")
    print("─" * 50 + "\n")
    
    # Pokreni server
    import uvicorn
    uvicorn.run(
        "web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Server zaustavljen. Doviđenja!")
    except Exception as e:
        print(f"\n❌ Greška: {e}")