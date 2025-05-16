from pathlib import Path
THIS = Path(__file__)           
WEBUI = THIS.parent.parent      
NERFROOT = WEBUI.parent / "nerfstudio"

import sys
sys.path.insert(0, str(WEBUI))
sys.path.insert(0, str(NERFROOT))
