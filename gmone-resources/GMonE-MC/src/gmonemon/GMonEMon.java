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

import gmonemon.plugin.*;

import java.io.*;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.util.Vector;

import common.*;

public class GMonEMon extends UnicastRemoteObject implements GMonEMonInterface, Serializable {

	private static final long serialVersionUID = 1L;
	String sHost;
	int iPort = 8649;
	Vector<GMonEMonPluginInterface> plugins = new Vector<GMonEMonPluginInterface>();

	public static String ruta;

	//----------------------------------------------------------
	// CLASS CONSTRUCTOR
	//----------------------------------------------------------

	@SuppressWarnings("rawtypes")
	public GMonEMon(String ssHost, String sRuta) throws RemoteException {

		super();
		sHost = ssHost;
		ruta = sRuta;
		String plugin = null;
		try {
			FileReader fr = new FileReader("plugins.list");
			BufferedReader br = new BufferedReader(fr);
			while (br.ready()){
				// Loading plugins
				try {
					plugin = br.readLine();
					Class c = Class.forName(plugin);
					GMonEMonPluginInterface cPlugin = (GMonEMonPluginInterface) c.newInstance();
					plugins.add(cPlugin);
					GMonELogger.message("Plugin "+plugin+" loaded");
				} catch (Exception e) {
					//e.printStackTrace();
					GMonELogger.message("WARNING: Error loading plugin "+plugin+" (not found)");
				}
			}
		} catch (Exception e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}


		// TODO Auto-generated constructor stub
	}

	//----------------------------------------------------------
	//Predefined Functions for the search
	//----------------------------------------------------------

	static double Max (Vector<GValue> vector){
		double max = -999999999, act;
		int i = 0;
		while (i < vector.size()){
			//Double d = (Double) vector.get(i);
			Double d = new Double(((GValue) vector.get(i)).sValue);
			act = d.doubleValue();
			if (act >= max){
				max = act;
			}
			i++;
		}
		return max;
	}

	static double Min (Vector<GValue> vector){
		double min = 999999999, act;
		int i = 0;
		while (i < vector.size()){
			//Double d = (Double) vector.get(i);
			Double d = new Double(((GValue) vector.get(i)).sValue);
			act = d.doubleValue();
			if (act <= min){
				min = act;
			}
			i++;
		}
		return min;
	}

	static double Sum (Vector<GValue> vector){
		double sum = 0, act;
		int i = 0;
		while (i < vector.size()){
			//Double d = (Double) vector.get(i);
			Double d = new Double(((GValue) vector.get(i)).sValue);
			act = d.doubleValue();
			sum = sum + act;
			i++;
		}
		return sum;
	}

	static double Prod (Vector<GValue> vector){
		double prod = 1, act;
		int i = 0;
		while (i < vector.size()){
			//Double d = (Double) vector.get(i);
			Double d = new Double(((GValue) vector.get(i)).sValue);
			act = d.doubleValue();
			prod = prod * act;
			i++;
		}
		//GMonELogger.message("P="+prod);
		return prod;
	}

	//----------------------------------------------------------
	//End of Predefined Functions for the search
	//----------------------------------------------------------

	static Vector<Double> vFilts (Vector<IO_Ganglia.CNode> vector, String param){
		Vector<Double> fil_val = new Vector<Double>();
		//IO_Ganglia iG = new IO_Ganglia();

		IO_Ganglia.CNode node;
		int i =0;

		while (i< vector.size()){
			Vector<IO_Ganglia.CMetric> params = new Vector<IO_Ganglia.CMetric>();
			node = (IO_Ganglia.CNode)vector.get(i);
			params = node.vMetrics;
			int j=0;
			IO_Ganglia.CMetric met;
			while (j<params.size()){
				met = (IO_Ganglia.CMetric) params.get(j);
				if (param.equals(met.sName)){
					Double d = Double.valueOf(Double.toString(met.sValue));
					fil_val.add(d);
				}
				j++;
			}
			i++;
		}
		return fil_val;
	}


	static String Compose (Vector<GValue> vector, String function){

		String sFunction= function;
		/*
	double max = Max(vector);
	double min = Min(vector);
	double sum = Sum(vector);
	double prod = Prod(vector);
		 */
		int n_elements = vector.size();

		/*
	System.out.println("P="+avoidScientificFormat(String.valueOf(prod)));

	sFunction = sFunction.replaceAll("S",String.valueOf(sum));
	sFunction = sFunction.replaceAll("P",avoidScientificFormat(String.valueOf(prod)));
	sFunction = sFunction.replaceAll("M",String.valueOf(max));
	sFunction = sFunction.replaceAll("m",String.valueOf(min));
	sFunction = sFunction.replaceAll("n",String.valueOf(n_elements));
		 */

		String sS = null;
		String sP = null;
		String sM = null;
		String sm = null;

		sFunction = "";

		for (int i = 0; i < function.length(); i++) {
			char actual = function.charAt(i);
			switch (actual) {
			case 'S': {
				if (sS == null) {
					double val = Sum(vector);
					sS = avoidScientificFormat(String.valueOf(val));
					//System.out.println("S = "+sS);
				}
				sFunction = sFunction+sS;
				break;
			}
			case 'P': {
				if (sP == null) {
					double val = Prod(vector);
					sP = avoidScientificFormat(String.valueOf(val));
					//System.out.println("P = "+sP);
				}
				sFunction = sFunction+sP;
				break;
			}
			case 'M': {
				if (sM == null) {
					double val = Max(vector);
					sM = avoidScientificFormat(String.valueOf(val));
					//System.out.println("M = "+sM);
				}
				sFunction = sFunction+sM;
				break;
			}
			case 'm': {
				if (sm == null) {
					double val = Min(vector);
					sm = avoidScientificFormat(String.valueOf(val));
					//System.out.println("m = "+sm);
				}
				sFunction = sFunction+sm;
				break;
			}
			case 'n': {
				sFunction = sFunction+n_elements;
				break;
			}
			default: {
				sFunction = sFunction+actual;
				break;
			}
			}
		}

		return sFunction;
	}


	static String avoidScientificFormat(String value) {

		String res = null;
		int pos = value.indexOf('E');

		if (pos == -1)
			res = value;
		else {
			String exp = value.substring(pos+1);
			res = "("+value.substring(0, pos);
			if (exp.charAt(0)=='-') {
				res = res+"/";
				exp = exp.substring(1);
			} else
				res = res+"*";
			int power = Integer.parseInt(exp);
			res = res+"1";
			for (int i = 0; i < power; i++)
				res = res+"0";
			res = res+")";

		}
		return res;
	}

	static void ParserWell (String function){

		String sFunction= function;

		sFunction = sFunction.replaceAll("S","1");
		sFunction = sFunction.replaceAll("P","1");
		sFunction = sFunction.replaceAll("M","1");
		sFunction = sFunction.replaceAll("m","1");
		sFunction = sFunction.replaceAll("n","1");

		Calc.resolver(sFunction);
	}




	//----------------------------------------------------------

	static String[] ReadFich (String nameFile){
		String[] metric;

		metric = new String[256];
		for (int i = 0; i < metric.length; i++)
			metric[i] = null;

		BufferedReader reader;
		try {
			reader = new BufferedReader(new FileReader(nameFile));
			try {
				String linea= reader.readLine();
				//String linea2= reader.readLine();
				int i=0;
				while(linea!=null) {
					if ((linea.charAt(0)!='#') && (linea.length()!=0))
						metric[i]=linea;
					//System.out.println(linea); 
					linea= reader.readLine();
					if(linea!=null)
						//	linea2= reader.readLine();
						i++;
				}
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		} catch (FileNotFoundException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}

		return metric;
	}


	//----------------------------------------------------------

	public static String Search (String param, String[] list){
		String function = null;
		int i=0, enc = 0;
		while (list[i]!=null && enc == 0){
			if (list[i].equals(param)){
				function=list[i+1];
				enc =1;
			}
			i=i+2;
		}
		return function;
	}

	//----------------------------------------------------------

	//It doesn't appear to write the params well, this could be because I'm not usuing
	//the file writer in the correct way. See FileWriter.
	public static void writeParams (String function, String parameter, String [] list){
		int i=0, enc = 0;
		while (list[i]!=null && enc == 0){
			if (list[i].equals(parameter)){
				list[i+1]=function;
				enc =1;
			}
			i=i+2;
		}

		try {
			//Writing the new configuration file with the predefined functions for all parameters
			Writer file = new FileWriter(ruta);
			i=0;
			while (list[i]!=null){
				file.write(list[i]);
				file.flush();
				file.write("\n");
				file.flush();
				i++;
			}
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	//----------------------------------------------------------
	// PUBLIC OPERATIONS
	//----------------------------------------------------------

	//Inserts a new parameter in the list to actualize the system (with the properly function)
	public void insertParam (String function, String parameter, String [] list) throws RemoteException {
		int i=0;
		while (list[i]!=null){
			i++;
		}
		list[i] = parameter;
		list[i+1] = function;
	}

	//----------------------------------------------------------

	//Function to change the value of the evaluation function for a parameter
	public void changeParam(String parameter, String function) throws RemoteException {
		String [] metric = ReadFich(ruta);
		if ("".equals(function)){
			//Then take the predefined function in params.txt
			function = "S";
			//function = Search(parameter, metric);
		}
		if ((Search(parameter, metric)).equals("-X")){
			try {
				insertParam(function, parameter, metric);
			} catch (RemoteException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		ParserWell(function);
		writeParams(function, parameter, metric);

	}

	//----------------------------------------------------------

	//Function that guives the complete list of parameters monitored by the plugins
	public Vector<String> getParamList() throws RemoteException {

		Vector<String> params = new Vector<String>();
		GMonEMonPluginInterface cPlugin = null;

		for (int i = 0; i < plugins.size(); i++) {
			cPlugin = (GMonEMonPluginInterface) plugins.elementAt(i);
			Vector<String> pars = cPlugin.getParams();	
			params.addAll(pars);
		}

		return params;
	}

	//----------------------------------------------------------

	//Client function which is used to get an aggregate value with a predefined funtion for a determinate 
	//parameter from the system

	// Devolveremos un vector de CValues
	public Vector<GValue> consult(String parameter) throws RemoteException {

		return consult(parameter, "");

	}

	// Client function which is used to get an aggregate value with a funtion for a determinate 
	// parameter from the system
	// Devolveremos un vector de CValues
	public Vector<GValue> consult(String parameter, String function) throws RemoteException {

		//String [] metric = ReadFich(ruta);
		Double consult;
		Vector<GValue> vConsult;
		GValue cV;

		GMonEMonPluginInterface cPlugin = findPlugin(parameter);

		//GMonELogger.message("GMonEMon: consulting "+parameter);

		if ("".equals(function)){
			//function = "((M+m)/2)";
			function = "N";
			//insertParam(function, parameter, metric);
		}

		Vector<GValue> vValues = null;

		if (cPlugin != null) {

			vValues = cPlugin.getValues(parameter);

		} else {

			//GMonELogger.message("GMonEMon: no se ha localizado plugin para "+parameter);

			//vValues = gangliaCons(parameter);
			vValues = new Vector<GValue>();

		}
		//Funcion NULA!!!!!!!!!!!!! No agrega
		if ("N".equals(function)){

			if (vValues.size() > 0) {
				//Se nos devulve directamente el Vector de CValues
				vConsult = vValues;

			} else {

				vConsult = new Vector<GValue>();

			}
		} else { //La funcion no es nula por lo tanto agregamos

			vConsult = new Vector<GValue>();

			if (vValues.size() > 0) {

				String calculum = Compose (vValues, function);

				consult = new Double(Calc.resolver(calculum));

				cV = new GValue();
				cV.sValue = consult.doubleValue();
				cV.sUnits = ((GValue)vValues.elementAt(vValues.size()-1)).sUnits;
				vConsult.add(cV);

			} else {

				consult = null;

			}
		}

		// Especificando el host en los CValues
		for (int i = 0; i < vConsult.size(); i++) {
			GValue val = (GValue) vConsult.elementAt(i);
			val.sHost = sHost;
		}
		return vConsult;

	}

	private GMonEMonPluginInterface findPlugin(String param) {

		GMonEMonPluginInterface cPlugin = null;

		int i = 0;
		boolean found = false;
		while ((i < plugins.size()) && (!found)) {

			//GMonELogger.message("GMonEMon: comprobando plugin "+i);

			cPlugin = (GMonEMonPluginInterface) plugins.elementAt(i);
			Vector<String> pars = cPlugin.getParams();

			int j = 0;
			boolean parFound = false;
			while ((j < pars.size()) && (!parFound)) {

				String p = (String)pars.elementAt(j);

				//GMonELogger.message("GMonEMon: comprobando parametro "+p);

				if (param.equals(p))
					parFound = true;
				else
					j++;

			}

			found = parFound;
			i++;

		}

		if (!found)
			cPlugin = null;

		return cPlugin;
	}

	// ---------------------------------------------------------
	// Publisher operations and atributes
	private int publishPeriod = 60;
	private String pubSubscriber = null;
	private Vector<GHost> subscribedParams = null;
	private Boolean publisherStarted = false;
	private Vector<String> subscriberURLs = null;


	public void startPublishingTo(String configFileName) {

		this.subscriberURLs = new Vector<String>();
		
		try{
			FileInputStream fstream = new FileInputStream(configFileName);
			DataInputStream in = new DataInputStream(fstream);
			BufferedReader br = new BufferedReader(new InputStreamReader(in));
			String strLine;
			//int lineNum = 0;
			//Read File Line By Line
			int configFileArea = 0; // 0 = subscriber names, 1 = parameters
			while ((strLine = br.readLine()) != null) {
				
				switch (configFileArea) {
				case 0 :
					// If the lie is a number, then it is the period.
					// Otherwise it is a subscriber name
					try {
						// If the line is not a number this will throw an exception.
						int possibleNum = Integer.parseInt(strLine);
						this.setPeriod(possibleNum);
						// Moving to the parameters area
						configFileArea = 1;
					} catch (NumberFormatException nfe) {
						if (! strLine.contains(":"))
							strLine = strLine + ":10990";
						this.subscriberURLs.add("//"+strLine+"/GMonEAccess");
						this.setSubscriberURL("//"+strLine+"/GMonEAccess"); // Temporary
					}
					break;
				case 1 :
					if (strLine.length() > 0) {
						String[] vals = strLine.split(":");
						this.publishParam(vals[0], vals[1]);
					}
				}
				
				/*
				if (lineNum == 0) {
					this.setSubscriberURL("//"+strLine+":10990/GMonEAccess");
				} else if (lineNum == 1) {
					this.setPeriod(Integer.parseInt(strLine));
				} else if (strLine.length() > 0) {
					String[] vals = strLine.split(":");
					this.publishParam(vals[0], vals[1]);
				}
				lineNum++;
				*/
			}
			//Close the input stream
			in.close();
			// Start publishing
			this.startPublisher();

		}catch (Exception e){//Catch exception if any
			e.printStackTrace();
		}

	}

	public void setPeriod(int period) throws RemoteException {
		publishPeriod = period;
	}

	public int getPeriod() throws RemoteException {
		return publishPeriod;
	}

	public void setSubscriberURL(String subscriber) throws RemoteException {
		pubSubscriber = subscriber;
	}

	public String getSubscriberURL() throws RemoteException {
		return pubSubscriber;
	}

	public Vector<String> getSubscriberURLs() throws RemoteException {
		return subscriberURLs;
	}

	public void publishParam(String param, String function) throws RemoteException {

		if (subscribedParams == null)
			subscribedParams = new Vector<GHost>();

		GHost ch = new GHost();
		ch.name = param;
		ch.func = function;

		subscribedParams.add(ch);
	}

	public Vector<GHost> getPublishedParams() throws RemoteException {
		return subscribedParams;
	}

	public void startPublisher() throws RemoteException {
		if (!publisherStarted) {
			publisherStarted = true;
			PublisherTMC publisher = new PublisherTMC(this, sHost);
			publisher.start();
		}
	}


	public void test(){
		try {
			GMonELogger.message((String.valueOf(this.getPeriod())));
		} catch (RemoteException e) {
			e.printStackTrace();
		}
	}

	public static void main(String[] args){
		try {
			GMonEMon g = new GMonEMon("localhost","monitor.conf");
			g.test();
		} catch (RemoteException e) {
			e.printStackTrace();
		}

	}

}
