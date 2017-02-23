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
	
package gmonemon.plugin;

import java.util.*;
import common.*;
import code.*;

public class DypapPlugin implements GMonEMonPluginInterface {

    private Monitor myMonitor;
    private Runtime runtime;

	public DypapPlugin() {

	    myMonitor = new Monitor();
	    myMonitor.startMonitor();
        runtime = Runtime.getRuntime();
	}

	public Vector<String> getParams() {

		Vector<String> v = new Vector<String>();
		String param = new String("dypap_cpu");
		v.add(param);

		return v;

	}

	public Vector<GValue> getValues(String param) {

		Vector<GValue> v = new Vector<GValue>();
		GValue cV = new GValue();
		cV.sName = param;
		if (param.equals("dypap_cpu")) {

		    cV.sValue = myMonitor.getAlphaValue();
		    cV.sUnits = new String(runtime.availableProcessors() +" cores");
		    v.add(cV);

		} 

		return v;
	}

}
