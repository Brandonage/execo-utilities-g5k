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

import org.jgroups.JChannel;
import org.jgroups.ReceiverAdapter;
import org.jgroups.Message;

import common.*;

public class UpdaterTMC extends ReceiverAdapter {

	String bindAddr;
	GMonEAccess access;
	
	public UpdaterTMC(GMonEAccess gmone, String host) {
		super();
		GMonELogger.message("Creating UpdaterTMC...");
		bindAddr = host;
		access = gmone;
	}
	
	public void init() {
		
		for (int i = 0; i < access.subscriptions.length; i++) {

			String publisher = access.subscriptions[i];
			GMonELogger.message("Subscribing to "+publisher);
			
			try {
				String gmoneMonPort = System.getenv("GMONEMON_PORT");
					if (gmoneMonPort == null)
						gmoneMonPort = "10991";
				System.setProperty("jgroups.bind_addr", bindAddr);
				System.setProperty("jgroups.tcpping.initial_hosts", publisher+"["+gmoneMonPort+"]");
				JChannel channel = new JChannel("jgroups.xml");
				channel.setReceiver(this);
				channel.connect("GMonEMon");
			} catch (Exception e) {
				e.printStackTrace();
			}
	        
		}
		
	}

	public void receive(Message msg) {
		GValue value = (GValue) msg.getObject();
		//GMonELogger.message("Message received "+value);
		access.storeSubscribedValue(value);
    }
}
