import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.services.photo_privacy import purge_expired
if __name__=='__main__':print('Capturas excluídas:',purge_expired())
