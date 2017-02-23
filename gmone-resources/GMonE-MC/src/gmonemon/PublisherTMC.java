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

import java.rmi.RemoteException;
import java.util.*;
import org.jgroups.JChannel;
import org.jgroups.Message;

import common.*;

public class PublisherTMC extends Thread {

	private GMonEMonInterface monitor;
	private String hostName;

	public PublisherTMC (GMonEMonInterface mon, String host) {
		monitor = mon;
		hostName = host;
	}

	public void run() {

		int period = 60;
		try {
			period = monitor.getPeriod();
		} catch (RemoteException e1) {
			e1.printStackTrace();
		}

		GMonELogger.message("Staring publisher...");

		GMonELogger.message("Creating channel...");
		
		JChannel channel = null;
		boolean configOk  = false;
		
		try {
			String gmoneMonPort = System.getenv("GMONEMON_PORT");
			if (gmoneMonPort == null)
				gmoneMonPort = "10991";
			// Comment the next line if running more than one GMonEMon per host (UDP only)
			System.setProperty("jgroups.bind_addr", hostName);
	        System.setProperty("jgroups.tcpping.initial_hosts", hostName+"["+gmoneMonPort+"]");
			channel = new JChannel("jgroups.xml");
			channel.setReceiver(null);
			channel.connect("GMonEMon");
			configOk  = true;
		} catch (Exception e) {
			e.printStackTrace();
		}

		while (configOk) {

			GMonELogger.message("Publishing parameters...");

			Vector<GValue> vals = new Vector<GValue>();
			
			long time1 = System.currentTimeMillis();
			try {
				Vector<GHost> parameters = monitor.getPublishedParams();					
				for (int j = 0; j < parameters.size(); j++) {
					GHost param = parameters.elementAt(j);
					Vector<GValue> currentVals = (Vector<GValue>) monitor.consult(param.name, param.func);
					for (int k = 0; k < currentVals.size(); k++) {
						GValue val = currentVals.elementAt(k);
						val.sName = param.name;
						vals.add(val);
						//GMonELogger.message("Publishing at " + time1 +val);
						//Message msg = new Message(null, null, val); We don't need a first message if we are going to send it in the next one
						//channel.send(msg);
					}
				}
			} catch (Exception e2) {
				e2.printStackTrace();
			}
			long time2 = System.currentTimeMillis();
			long monitorTime = time2-time1;
			GMonELogger.message("Monitor time: "+monitorTime+" ms");
			try {
				for (int k = 0; k < vals.size(); k++) {
					GValue val = vals.elementAt(k);
					Message msg = new Message(null, null, val);
					GMonELogger.message("Publishing at " + time2 +val);
					channel.send(msg);
				}
			} catch (Exception e2) {
				e2.printStackTrace();
			}
			// Sleeping for the time period
			long time3 = System.currentTimeMillis();
			long publishTime = time3-time2;			
			long timeDiff = time3 - time1;
			GMonELogger.message("Publish time: "+publishTime+" ms");
			try {
				GMonELogger.message("Waiting "+period+" seconds...");
				Thread.sleep((period*1000)-timeDiff);
			} catch (Exception e3) {
				e3.printStackTrace();
			}

		}

	}

}
