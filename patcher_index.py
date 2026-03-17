# =============================================================================
# patcher_index.py
# =============================================================================
# Applique les modifications de l'interface pour le nouveau referentiel attendus.
# A lancer une seule fois depuis le dossier _OUTIL.
# Modifie static/index.html en place.
# =============================================================================

from pathlib import Path
import shutil

INDEX_PATH = Path(__file__).parent / "static" / "index.html"

if not INDEX_PATH.exists():
    print(f"ERREUR : {INDEX_PATH} introuvable.")
    exit(1)

# Sauvegarde
shutil.copy2(INDEX_PATH, INDEX_PATH.with_suffix(".html.bak"))
print(f"Sauvegarde : {INDEX_PATH.with_suffix('.html.bak')}")

html = INDEX_PATH.read_text(encoding="utf-8")

# ============================================================
# PATCH 1 : buildAttendusAccordion — ajout du point couleur
# ============================================================
OLD_LABEL = (
    "            lbl.innerHTML = '<input type=\"checkbox\" name=\"attendu\" value=\"' + a.id + '\"> "
    "<span>' + sd + a.libelle + '</span>';"
)
NEW_LABEL = (
    "            var typeColor = (a.type === 'disciplinaire') ? '#7B6EE0' : '#4a7c59';\n"
    "            var dot = '<span style=\"display:inline-block;width:7px;height:7px;border-radius:50%;"
    "background:'+typeColor+';flex-shrink:0;margin:3px 3px 0 0\"></span>';\n"
    "            lbl.innerHTML = '<input type=\"checkbox\" name=\"attendu\" value=\"' + a.id + '\"> ' "
    "+ dot + ' <span>' + sd + a.libelle + '</span>';"
)

if OLD_LABEL in html:
    html = html.replace(OLD_LABEL, NEW_LABEL, 1)
    print("PATCH 1 OK : point couleur dans le filtre sidebar")
else:
    print("PATCH 1 : chaine non trouvee — verifier manuellement")

# ============================================================
# PATCH 2 : buildDrawer — attendus melanges par domaine
# ============================================================
OLD_ATTENDUS = """  var edd_at=(a.attendus||[]).filter(function(at){return !at.type||at.type==='EDD';});
  var disc_at=(a.attendus||[]).filter(function(at){return at.type==='disciplinaire';});
  function fmtAttendus(items, badgeBg, badgeColor){
    if(!items.length) return '<span style="color:var(--text-muted);font-size:.82rem">—</span>';
    var byCycle={};
    items.forEach(function(at){ if(!byCycle[at.cycle_code]) byCycle[at.cycle_code]=[]; byCycle[at.cycle_code].push(at); });
    var s='';
    Object.keys(byCycle).forEach(function(code){
      s+='<div class="attendu-cycle-title">'+code+'</div>';
      byCycle[code].forEach(function(at){
        var sd=at.sous_domaine?'<strong>'+at.sous_domaine+'</strong> — ':'';
        var style=badgeBg?'style="background:'+badgeBg+';color:'+badgeColor+'"':'';
        s+='<div class="attendu-row"><span class="badge attendu-dom" '+style+'>'+at.domaine+'</span><span>'+sd+at.libelle+'</span></div>';
      });
    });
    return s;
  }
  h+=`<div class="drawer-section"><h3>Attendus EDD</h3>`+fmtAttendus(edd_at,'','')+'</div>';
  h+=`<div class="drawer-section"><h3>Attendus disciplinaires</h3>`+fmtAttendus(disc_at,'#EEEDFE','#534AB7')+'</div>';"""

NEW_ATTENDUS = """  // Attendus melanges par domaine, code couleur par type
  function fmtAttendus(items){
    if(!items||!items.length) return '<span style="color:var(--text-muted);font-size:.82rem">—</span>';
    // Grouper par cycle puis domaine
    var byCycle={};
    items.forEach(function(at){
      if(!byCycle[at.cycle_code]) byCycle[at.cycle_code]={};
      var dom=at.domaine||'Autre';
      if(!byCycle[at.cycle_code][dom]) byCycle[at.cycle_code][dom]=[];
      byCycle[at.cycle_code][dom].push(at);
    });
    var s='';
    Object.keys(byCycle).sort().forEach(function(code){
      s+='<div class="attendu-cycle-title">'+code+'</div>';
      var byDom=byCycle[code];
      Object.keys(byDom).sort().forEach(function(dom){
        byDom[dom].forEach(function(at){
          var sd=at.sous_domaine?'<strong>'+at.sous_domaine+'</strong> — ':'';
          var isEDD=!at.type||at.type==='EDD';
          var dotColor=isEDD?'#4a7c59':'#7B6EE0';
          var badgeBg=isEDD?'':'#EEEDFE';
          var badgeColor=isEDD?'':'#534AB7';
          var style=badgeBg?'style="background:'+badgeBg+';color:'+badgeColor+'"':'';
          var dot='<span title="'+(isEDD?'EDD':'Disciplinaire')+'" style="display:inline-block;width:8px;height:8px;border-radius:50%;background:'+dotColor+';flex-shrink:0;margin:3px 4px 0 0"></span>';
          s+='<div class="attendu-row">'+dot+'<span class="badge attendu-dom" '+style+'>'+dom+'</span><span>'+sd+at.libelle+'</span></div>';
        });
      });
    });
    return s;
  }
  h+=`<div class="drawer-section"><h3>Attendus <span style="font-size:.68rem;margin-left:6px;opacity:.7">` +
    `<span style="display:inline-flex;align-items:center;gap:3px"><span style="width:8px;height:8px;border-radius:50%;background:#4a7c59;display:inline-block"></span>EDD</span>` +
    `&nbsp;&nbsp;<span style="display:inline-flex;align-items:center;gap:3px"><span style="width:8px;height:8px;border-radius:50%;background:#7B6EE0;display:inline-block"></span>Disciplinaire</span>` +
    `</span></h3>`+fmtAttendus(a.attendus)+'</div>';"""

if OLD_ATTENDUS in html:
    html = html.replace(OLD_ATTENDUS, NEW_ATTENDUS, 1)
    print("PATCH 2 OK : attendus melanges par domaine avec points couleur")
else:
    print("PATCH 2 : chaine non trouvee — verifier manuellement")
    # Aide au diagnostic
    if "fmtAttendus" in html:
        print("  -> 'fmtAttendus' existe dans le fichier")
    if "Attendus EDD" in html:
        print("  -> 'Attendus EDD' existe dans le fichier")

# Ecriture
INDEX_PATH.write_text(html, encoding="utf-8")
print(f"\nFichier modifie : {INDEX_PATH}")
print("Verifiez le rendu dans le navigateur avant de commiter.")
