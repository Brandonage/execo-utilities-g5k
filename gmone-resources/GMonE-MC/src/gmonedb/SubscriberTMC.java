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

import java.rmi.*;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.Vector;
import common.*;

public class SubscriberTMC extends Thread {

	private int periodo; // Periodo de muestreo
	private DBAccessInterface bd; // Objeto de acceso a la base de datos
	//String ficheroBD = "GMonE2";
	String ssHost = "localhost";

	GMonEAccess access = null;

	public SubscriberTMC (GMonEAccess gmone, DBAccessInterface db)  {

		//ficheroBD = dbName;
		//bd = new DBAccessSQL("org.sqlite.JDBC", "jdbc:sqlite:"+ficheroBD);
		this.bd = db;

		access = gmone;

	}

	public void setPeriod(int tiempo) {

		try {
			periodo = tiempo;
		} catch (RuntimeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	/*
	public Vector<GHost> getConfiguration(){
		int i=0;
		Vector<GHost> res = bd.leerParametros();
		while (i < res.size()){
			GMonELogger.message("PARAM: "+((GHost)res.get(i)).name+", HOST: "+((GHost)res.get(i)).host+", FUNCTION: "+((GHost)res.get(i)).func+"\n");
			i = i+1;
		}
		return res;
	}
	*/
	public int getPeriod() throws RemoteException {
		return periodo;
	}	

	// ----------------------------------------------------------------------------------------------
	public void consultarMon() {

		try {

			Vector<GValue> vVals = access.getSubscribedValues();
			Vector<GValue> filtVals = new Vector<GValue>();
			
			for (int i = 0; i < vVals.size(); i++) {
				GValue val = vVals.elementAt(i);
				if (!filtVals.contains(val))
					filtVals.add(val);
				//else
				//	GMonELogger.message("Discarding repeated "+val);
			}
			
			//GMonELogger.message("Discarded "+(vVals.size()-filtVals.size())+" repeated values.");
			
			bd.exeMultipleWrite(filtVals);

		} catch (Exception e1) {
			e1.printStackTrace();
		}
	}

	public void changeParameter (String sNombre, String sFuncion, String sHost){
		bd.changeP(sNombre, sFuncion, sHost);
	}

	public void run() {

		String gmoneDBPort = System.getenv("GMONEDB_PORT");
		if (gmoneDBPort == null)
			gmoneDBPort = "10990";
		int regPort = Integer.parseInt(gmoneDBPort);
		Registry reg = null;
		try {
			System.setProperty("java.net.preferIPv4Stack", "true");
			System.setProperty("java.rmi.server.hostname", access.ssHost);
			GMonELogger.message("Creating RMI registry at port "+regPort+"...");
            reg = LocateRegistry.createRegistry(regPort);
		} catch (Exception e) {
            GMonELogger.message("Registry cannot be created (maybe it is already running?)");
            //e.printStackTrace();                                                                                                         
		}
		try {
			GMonELogger.message("Binding GMonEAccess object...");
			if (reg == null) {
				reg = LocateRegistry.getRegistry(regPort);
		    }
			reg.rebind("GMonEAccess", access);
		} catch (Exception e) {
			e.printStackTrace();
		}

		// -----------------------------------
		// Gathering published information
		while (true) {	
			long time1 = System.currentTimeMillis();
			try {
				consultarMon();
			} catch (Exception e2) {
				e2.printStackTrace();
			}
			long time2 = System.currentTimeMillis();
			long timeDiff = time2-time1;
			try {
				GMonELogger.message("Archive time: "+timeDiff+" ms");
				GMonELogger.message("Waiting "+getPeriod()+" seconds...");
				Thread.sleep((getPeriod()*1000)-timeDiff);
			} catch (Exception e3) {
				e3.printStackTrace();
			}
		}
	}
}
