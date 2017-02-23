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

package gmonemon;

//import java.rmi.Naming;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

import common.*;

public class GMonEMonService {

	public GMonEMonService() {
		super();
	}

	public static void main(String[] args) {
		
		if (args.length < 1) {
			System.out.println("Parameters: host [config_file]");
			return;
		}
		
		try {
			String sHost = args[0];
			String sRuta = "";
			GMonELogger.message("Starting GMonEMon...");
			GMonEMon obj = new GMonEMon(sHost, sRuta);
			GMonELogger.message("...GMonEMon running");
			if (args.length >= 2) {
				String configFileName = args[1];
				obj.startPublishingTo(configFileName);
				GMonELogger.message(String.valueOf(obj.getPeriod()));
			} else {
				String gmoneMonPort = System.getenv("GMONEMON_PORT");
				if (gmoneMonPort == null)
					gmoneMonPort = "10990";
				int regPort = Integer.parseInt(gmoneMonPort);
				Registry reg = null;
				try {
					GMonELogger.message("Creating RMI registry at port "+regPort+"...");
		            reg = LocateRegistry.createRegistry(regPort);
				} catch (Exception e) {
		            GMonELogger.message("Registry cannot be created (maybe it is already running?)");
		            //e.printStackTrace();                                                                                                         
				}
				GMonELogger.message("Binding GMonEMon object...");
				if (reg == null) {
					reg = LocateRegistry.getRegistry(regPort);
			    }
				//Naming.rebind("//localhost:10990/GMonEMon", obj);
				reg.rebind("GMonEMon", obj);
			}

		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
	}
}
