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

import gmonemon.plugin.IO_Ganglia.CMetric;
import gmonemon.plugin.IO_Ganglia.CNode;

import java.util.*;
import java.io.*;

import common.*;

public class GangliaPlugin implements GMonEMonPluginInterface {

	public static String ruta;

	String sHost = "localhost";
	int iPort = 8649;

	Vector<String> vNodesSelected = new Vector<String>();

	//-----------------------------------------------------------------

	public GangliaPlugin() {

		String fileName = "Plugins/nodes.list"; 
		BufferedReader bf = null;

		try {
			bf = new BufferedReader (new FileReader (fileName));
			while (bf.ready()){
				String node = new String(bf.readLine());
				vNodesSelected.add(node);
			}
		} catch (FileNotFoundException e) {
			System.out.println("GangliaPlugin: ATENCION. No se encuentra el"+
					" fichero de nodes "+fileName+".");
		} catch (IOException e2) {
			System.out.println("GangliaPlugin: ATENCION. No se puede leer el"+
					" fichero de nodes "+fileName+".");
		} 

	}

	//-----------------------------------------------------------------

	private boolean validateNode(String node) {

		int i = 0;
		boolean found = true;

		if (vNodesSelected.size() != 0) {
			do {   
				String sThisNode = (String) vNodesSelected.elementAt(i);

				found = sThisNode.equals(node);
				i++;
			} while ((i < vNodesSelected.size()) && !found);
		}

		return found;
	}

	//-----------------------------------------------------------------

	public Vector<String> getParams() {

		//Acces to ganglia metrics and composing of the results vector

		IO_Ganglia iG = new IO_Ganglia(sHost, iPort, ruta);
		Vector<CNode> vNodes = new Vector<CNode>();

		BufferedReader bBuffer = iG.TcpCmd( sHost, iPort, "" );

		if ( bBuffer  == null ) {
			System.out.println ( " Failed  to get the the Ganglia output " );
		}

		try {
			vNodes = iG.Parse (bBuffer);
		} catch (Exception e) {
			e.printStackTrace();
		}

		//Filtering the interesting values for the parameter of the consult

		//System.out.println("Obtained information from "+vNodes.size()+" nodes");

		Vector<String> vFilter = new Vector<String>();
		vFilter = vFiltParams (vNodes);

		return vFilter;

	}    

	//-----------------------------------------------------------------

	public Vector<GValue> getValues(String param) {

		//Acces to ganglia metrics and composing of the results vector

		//System.out.println("GangliaPlugin: consultando "+param+" de nodo "+sNodeSelected);

		IO_Ganglia iG = new IO_Ganglia(sHost, iPort, ruta);
		Vector<CNode> vNodes = new Vector<CNode>();

		BufferedReader bBuffer = iG.TcpCmd ( sHost, iPort, "" );

		if ( bBuffer  == null ) {
			System.out.println ( " Failed  to get the the Ganglia output " );
		}

		try {
			vNodes = iG.Parse (bBuffer);
		} catch (Exception e) {
			e.printStackTrace();
		}

		//Filtering the interesting values for the parameter of the consult

		Vector<GValue> vFilter = new Vector<GValue>();
		vFilter = vFiltValues (vNodes, param);       	

		return vFilter;

	}

	//-----------------------------------------------------------------

	Vector<GValue> vFiltValues (Vector<CNode> vector, String param) {
		Vector<GValue> fil_val = new Vector<GValue>();
		//IO_Ganglia iG = new IO_Ganglia();

		IO_Ganglia.CNode node;
		int i =0;

		while (i< vector.size()){
			Vector<CMetric> params = new Vector<CMetric>();
			node = (IO_Ganglia.CNode)vector.get(i);

			//System.out.print("Reading node "+node.NodeName+"...");

			if (validateNode(node.NodeName)) {

				//System.out.println("ok");

				params = node.vMetrics;
				int j=0;
				IO_Ganglia.CMetric met;
				while (j<params.size()){
					met = (IO_Ganglia.CMetric) params.get(j);
					if (param.equals(met.sName)){
						Double d = Double.valueOf(Double.toString(met.sValue));
						GValue cV = new GValue();
						cV.sValue = d.doubleValue();
						cV.sUnits = new String(met.sUnits);
						fil_val.add(cV);
					}
					j++;
				}
			} /* else
		 System.out.println("ignored"); */

			i++;
		}
		return fil_val;
	}

	//-----------------------------------------------------------------

	Vector<String> vFiltParams (Vector<CNode> vector){
		Vector<String> fil_pars = new Vector<String>();
		//IO_Ganglia iG = new IO_Ganglia();

		IO_Ganglia.CNode node;
		int i =0;

		while (i< vector.size()){
			Vector<CMetric> params = new Vector<CMetric>();
			node = (IO_Ganglia.CNode)vector.get(i);

			if (validateNode(node.NodeName)) {
				params = node.vMetrics;
				//System.out.println("node "+node.NodeName+" ("+params.size()+" params)");
				int j=0;
				IO_Ganglia.CMetric met;
				while (j<params.size()) {
					met = (IO_Ganglia.CMetric) params.get(j);
					//System.out.println("\tparameter "+met.sName);
					if (!fil_pars.contains(met.sName)) {
						String p = new String(met.sName);
						fil_pars.add(p);
					}
					j++;
				}
			}

			i++;
		}
		return fil_pars;
	}
}
