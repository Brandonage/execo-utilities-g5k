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
import java.io.*;
import common.*;

public class BasicLinuxPlugin implements GMonEMonPluginInterface {

	public BasicLinuxPlugin() {
	}

	public Vector<String> getParams() {

		Vector<String> v = new Vector<String>();
		v.add("cpu_load1");
		v.add("cpu_load5");
		v.add("cpu_load15");
		v.add("cpu_usage");
		v.add("mem_total");
		v.add("mem_free");
		v.add("mem_usage");
		return v;

	}

	public Vector<GValue> getValues(String param) {

		Vector<GValue> v = new Vector<GValue>();
		GValue cV = new GValue();
		cV.sName = param;
		if (param.equals("cpu_load1")) {

			Vector<Double> vals = readLoadValues();
			cV.sValue = ((Double) vals.elementAt(0)).doubleValue();
			v.add(cV);

		} else if (param.equals("cpu_load5")) {

			Vector<Double> vals = readLoadValues();
			cV.sValue = ((Double) vals.elementAt(1)).doubleValue();
			v.add(cV);

		} else if (param.equals("cpu_load15")) {

			Vector<Double> vals = readLoadValues();
			cV.sValue = ((Double) vals.elementAt(2)).doubleValue();
			v.add(cV);

		} else if (param.equals("cpu_usage")) {

			Vector<Double> vals = readCPUValues();
			cV.sValue = ((Double) vals.elementAt(0)).doubleValue();
			cV.sUnits = "%";
			v.add(cV);

		} else if (param.equals("mem_total")) {

			Vector<Double> vals = readMemValues();
			cV.sValue = ((Double) vals.elementAt(0)).doubleValue();
			cV.sUnits = "kB";
			v.add(cV);

		} else if (param.equals("mem_free")) {

			Vector<Double> vals = readMemValues();
			cV.sValue = ((Double) vals.elementAt(1)).doubleValue();
			cV.sUnits = "kB";
			v.add(cV);
			
		} else if (param.equals("mem_usage")) {

			Vector<Double> vals = readMemValues();
			Double total = ((Double) vals.elementAt(0)).doubleValue();
			Double used = total - ((Double) vals.elementAt(1)).doubleValue();
			cV.sValue = new Double((used*100.0)/total);
			cV.sUnits = "%";
			v.add(cV);
			
		} 

		return v;
	}

	private Vector<Double> readLoadValues() {

		Vector<Double> results = new Vector<Double>();
		FileReader fr;
		try {
			fr = new FileReader("/proc/loadavg");
			BufferedReader br = new BufferedReader(fr);
			String line = br.readLine();
			String[] tokens = line.split("\\s+");
			results.add(Double.parseDouble(tokens[0]));
			results.add(Double.parseDouble(tokens[1]));	
			results.add(Double.parseDouble(tokens[2]));	
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return results;
	}

	private Vector<Double> readCPUValues() {

		Vector<Double> results = new Vector<Double>();

		try {
            Process child = Runtime.getRuntime().exec("./cpu_usage.py");
            child.waitFor();
            BufferedInputStream childOutput = (BufferedInputStream) child.getInputStream();
            int val = childOutput.read();
            String value = "";
            while (val != -1) {
                char c = (char)val;
                if ((c != ' ') && (c != '\n'))
                    value = value + c;
                else {
                    results.add(Double.parseDouble(value));
                    value = "";
                }
                val = childOutput.read();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return results;
	}

	private Vector<Double> readMemValues() {

		Vector<Double> results = new Vector<Double>();
		FileReader fr;
		try {
			fr = new FileReader("/proc/meminfo");
			BufferedReader br = new BufferedReader(fr);
			String line = br.readLine();
			String[] tokens = line.split("\\s+");
			results.add(Double.parseDouble(tokens[1]));
			line = br.readLine();
			tokens = line.split("\\s+");
			results.add(Double.parseDouble(tokens[1]));			
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return results;
	}


	public void test() {
		GMonELogger.message("Reading load values...");
		GMonELogger.message("LOAD: "+this.readLoadValues());
		GMonELogger.message("MEM: "+this.readMemValues());
		GMonELogger.message("Values read...");	
	}

	public static void main(String[] args) {
		BasicLinuxPlugin p = new BasicLinuxPlugin();
		p.test();
	}

}
