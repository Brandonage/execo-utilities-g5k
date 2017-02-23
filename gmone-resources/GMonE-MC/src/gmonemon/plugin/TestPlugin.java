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

public class TestPlugin implements GMonEMonPluginInterface {

	public TestPlugin() {
	}

	public Vector<String> getParams() {

		Vector<String> v = new Vector<String>();
		String param = new String("test_param_1");
		v.add(param);
		param = new String("test_param_2");
		v.add(param);

		return v;

	}

	public Vector<GValue> getValues(String param) {

		Vector<GValue> v = new Vector<GValue>();
		GValue cV = new GValue();
		if (param.equals("test_param_1")) {

			cV.sValue = (new Double(1.0)).doubleValue();
			cV.sInfo = new String("test_param_val_1");
			cV.sUnits = new String("gallifantes");
			v.add(cV);
			cV = new GValue();
			cV.sValue = (new Double(2.0)).doubleValue();
			cV.sInfo = new String("test_param_val_2");
			cV.sUnits = new String("gallifantes");
			v.add(cV);

		} else if (param.equals("test_param_2")) {

			Random cR = new Random();

			for (int i = 0; i < 10; i++) {

				cV = new GValue();
				cV.sValue = cR.nextDouble();
				cV.sInfo = new String("test_param_val_"+i);
				cV.sUnits = new String("gallifantes");
				v.add(cV);

			}
		}

		return v;
	}

}
