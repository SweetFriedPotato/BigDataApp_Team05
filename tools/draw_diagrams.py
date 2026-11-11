#!/usr/bin/env python3
"""Original vector diagrams of the actual schema and request flow; no external renderer."""
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'docs/diagrams';D.mkdir(exist_ok=True)
def box(x,y,w,h,title,lines):
    content=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#fffefb" stroke="#bccbb9"/><rect x="{x}" y="{y}" width="{w}" height="32" rx="6" fill="#2c6155"/><text x="{x+12}" y="{y+22}" fill="white" font-weight="bold">{escape(title)}</text>'
    for i,line in enumerate(lines):content+=f'<text x="{x+12}" y="{y+54+i*19}" fill="#233b37">{escape(line)}</text>'
    return content
start='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 780" role="img" aria-label="Six-table ERD"><rect width="1000" height="780" fill="#f7f5ef"/><g font-family="Arial,sans-serif" font-size="13">'
svg=start
svg+=box(20,30,280,195,'locations',['PK location_id','UK location_code','name_en / name_ko','requested_latitude','requested_longitude'])
svg+=box(370,30,290,195,'daily_temperatures',['PK, FK location_id','PK weather_date (LST)','tmean / tmax / tmin (DECIMAL)','CHECK pairwise temperature order','INDEX weather_date, location_id'])
svg+=box(20,310,280,245,'saved_plans',['PK plan_id','plan_name','start_date / end_date','max_temp_threshold','max_temp_range','memo','created_at / updated_at'])
svg+=box(370,310,290,150,'plan_locations',['PK, FK plan_id (CASCADE delete)','PK, FK location_id','INDEX location_id'])
svg+=box(700,310,280,150,'solar_terms',['PK term_date','term_name (repeats by year)','source_url','Calendar reference: no FK'])
svg+=box(700,520,280,165,'monthly_food_guides',['PK guide_id','UK month_no + food_name','source_url','CHECK month between 1 and 12','Monthly reference: no FK'])
svg+='<g stroke="#b45b3b" stroke-width="2" fill="none"><path d="M300 95 H370"/><path d="M160 225 V275 H515 V310"/><path d="M300 380 H370"/></g><g fill="#b45b3b" font-size="12"><text x="306" y="83">1 → many</text><text x="318" y="266">1 → many</text><text x="305" y="365">1 → many</text></g><text x="20" y="620">Physical FKs: weather→locations; plan_locations→plans and locations.</text><text x="20" y="647">At least one location per plan is an application + transaction invariant.</text><text x="20" y="674">Solar terms and food guides use independent date/month lookups.</text><text x="20" y="701">All six tables: InnoDB, utf8mb4_unicode_ci. Exactly six BASE TABLEs.</text></g></svg>'
(D/'erd.svg').write_text(svg)
svg=start.replace('Six-table ERD','PHP request and database flow')
svg+=box(20,20,280,100,'Browser input',['GET analysis forms','POST plan/reset forms + CSRF'])
svg+=box(360,20,280,100,'bootstrap.php',['config + Session + escaping','strict native PDO connection'])
svg+=box(700,20,280,100,'filters.php / session.php',['strict dates, decimals, IDs','atomic Session update'])
svg+=box(20,230,280,135,'Analysis pages',['aggregate / olap / ranking / window','queries.php: CTEs + prepared SQL','temperature calculations in DB'])
svg+=box(360,230,280,135,'Plan pages and actions',['list / form / detail','POST actions + validated apply','repository transaction + PRG'])
svg+=box(700,230,280,135,'Seasonal page',['year/month selection','independent prepared SELECTs','source URLs displayed'])
svg+=box(200,480,600,110,'MariaDB — team05 account',['six InnoDB tables; constraints + indexed dates','COMMIT complete writes; ROLLBACK intermediate failures'])
svg+=box(200,665,600,80,'View + header + footer',['escaped tables; separate menus; local CSS/JS/fonts'])
svg+='<g stroke="#b45b3b" stroke-width="2" fill="none"><path d="M300 65 H360"/><path d="M640 65 H700"/><path d="M840 120 V170 H160 V230"/><path d="M500 170 V230"/><path d="M840 170 V230"/><path d="M160 365 V430 H500 V480"/><path d="M500 365 V480"/><path d="M840 365 V430 H500"/><path d="M500 590 V665"/></g></g></svg>'
(D/'php-structure.svg').write_text(svg)
print('Two original SVG diagrams generated from actual table/file relationships')
