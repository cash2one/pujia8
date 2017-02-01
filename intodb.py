import sqlite3,Pluto
conn = sqlite3.connect('translate.db')
cu = conn.cursor()
fl = Pluto.walk('webappimg')
for i,fn in enumerate(fl):
    cu.execute('insert into webapp_chungu values(%d,"%s","name",3,3,3,3,"shuoming",1)'%(i+1,fn.replace('\\','/')))
conn.commit()
