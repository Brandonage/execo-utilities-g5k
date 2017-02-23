/******************************************************************************
 * 
 *  GMonE: A customizable monitoring tool for distributed systems
 *  Copyright (C) 2010  Jesus Montes
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *  
 *****************************************************************************/

package gmonedb;

import java.net.MalformedURLException;
import java.rmi.Naming;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.util.Vector;
import common.*;

public class GMonET extends Thread {

	private int periodo; // Periodo de muestreo
	public Vector<GHost> params; // Vector de par?metros que se desean monitorizar
	private DBAccessSQL bd; // Objeto de acceso a la base de datos
	String ficheroBD = "GMonE2";
	String ssHost = "localhost";

	public void setPeriod(int tiempo) {

		try {
			periodo = tiempo;
		} catch (RuntimeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public Vector<GHost> getConfiguration(){
		int i=0;
		Vector<GHost> res = bd.leerParametros();
		while (i < res.size()){
			GMonELogger.message("PARAM: "+((GHost)res.get(i)).name+", HOST: "+((GHost)res.get(i)).host+", FUNCTION: "+((GHost)res.get(i)).func+"\n");
			i = i+1;
		}
		return res;
	}


	//public GMonEDB (int p, int in, String ficheroHostsMonALISA, String ficheroBD) throws RemoteException {
	//public GMonEAccess (String ficheroBD, String ssHost)  {
	//public GMonEAccess ()  {
	public GMonET (String dbName)  {

		ficheroBD = dbName;

		//System.out.println ("Almacenando en la base de datos "+ficheroBD+"...");
		//bd = new DBAccessSQL("com.mysql.jdbc.Driver", "jdbc:mysql://"+sHostDB+"/"+ficheroBD);
		bd = new DBAccessSQL("org.sqlite.JDBC", "jdbc:sqlite:"+ficheroBD);

	}
	public int getPeriod() throws RemoteException {
		return periodo;
	}	

	// ----------------------------------------------------------------------------------------------
	public int consultarMon(String ficheroBD, long time) {
		//bd = new DBAccessSQL("com.mysql.jdbc.Driver", "jdbc:mysql://madreselva/"+ficheroBD);
		//bd = new DBAccessSQL("com.mysql.jdbc.Driver", "jdbc:mysql://localhost/"+ficheroBD);
		//bd.ejemplo();
		params = bd.leerParametros();
		String parametro="";
		String host="";
		String func="";
		int rs=0;

		// No podemos hacerlo aqui: bd.conectarDB();

		int i=0;
		while (i< params.size()){
			parametro = ((GHost)params.get(i)).name;
			host = ((GHost)params.get(i)).host;
			func = ((GHost)params.get(i)).func;
			System.out.print("("+host+", "+parametro+", "+func+")\t->");
			try {
				String gmoneMonPort = System.getenv("GMONEMON_PORT");
				if (gmoneMonPort == null)
					gmoneMonPort = "10990";
				//GMonEMonInterface m = (GMonEMonInterface) Naming.lookup("//localhost/GMonEMon");
				GMonEMonInterface m = (GMonEMonInterface) Naming.lookup("//"+host+":"+gmoneMonPort+"/GMonEMon");
				/*
		  Double conRes = m.Consult(parametro, func);
		  if (conRes != null) {
		  valor = conRes.doubleValue();
		  //valor = (long) m.Consult(parametro, "");
		  rs = bd.exeQueryWrite (parametro, valor, time, host);
		  //rs = this.stmt.executeUpdate(query);
		  System.out.println(valor);
		  }
				 */
				Vector<GValue> vVals = m.consult(parametro, func);
				for (int j = 0; j < vVals.size(); j++) {
					GValue cV = (GValue) vVals.elementAt(j);
					rs = bd.exeQueryWrite (parametro, cV.sValue, time, host, cV.sInfo, cV.sUnits);
					System.out.print("\t("+cV.sValue+", "+cV.sInfo+")");
				}
				System.out.print("\n");
			} catch (MalformedURLException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			} catch (RemoteException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			} catch (NotBoundException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}

			i++;
			/*while (rs.next()){
	      i++;
	      System.out.println("\nEl valor "+i+" es "+rs.getString("name")+"\n");
	      }*/

		}

		return rs;
		//bd.ejecutar(params, time);
	}

	public void changeParameter (String sNombre, String sFuncion, String sHost){
		bd.changeP(sNombre, sFuncion, sHost);
	}

	/*public GMonET() {
      super();
      // TODO Auto-generated constructor stub
      }*/

	public static void main(String[] args) {

	}

	public void run() {

		try {
			while (true) {
				// Se consultan los par?metros
				long tiempoKK = System.currentTimeMillis();
				//obj.consultarMonALISA();
				//Aqui hacemos la consulta a todo el sistema... Debemos implemetarlo en GMonEDB
				//obj.consultarMonALISA();
				consultarMon(ficheroBD, tiempoKK);
				GMonELogger.message("Query time: "+(System.currentTimeMillis()-tiempoKK)+" ms");
				// Se espera el n?mero de segundos indicado en la configuraci?n
				GMonELogger.message("Waiting "+getPeriod()+" seconds...");
				Thread.sleep(getPeriod()*1000);
			}
		} catch (RemoteException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
