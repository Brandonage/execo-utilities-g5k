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
import java.text.*;
import java.util.regex.*;
import common.*;

public class BlobSeerProviderPlugin implements GMonEMonPluginInterface {

	// ---------------------------------------------
	// Predefined constants and internal structures
	private String logFile = "Plugins/provider_output.log";
	//private String[] acceptedCommands = {"RPS", "WPS", "FSC"};
	// ---------------------------------------------
	// Class attributes
	private BufferedReader logBuffer;
	private Vector<GValue> readLogs;
	private Vector<GValue> writeLogs;
	private Vector<GValue> spaceLogs;
	private Vector<GValue> inLogs;
	private Vector<GValue> outLogs;
	// ---------------------------------------------

	// ---------------------------------------------
	// Main methods
	// ---------------------------------------------

	public BlobSeerProviderPlugin() {

		logBuffer = openLogFile(logFile);
		readLogs = new Vector<GValue>();
		writeLogs = new Vector<GValue>();
		spaceLogs = new Vector<GValue>();
		inLogs = new Vector<GValue>();
		outLogs = new Vector<GValue>();

	}

	// ---------------------------------------------

	public Vector<String> getParams() {

		Vector<String> v = new Vector<String>();
		// Basic parameters
		v.add("cpu_load1");
		v.add("cpu_load5");
		v.add("cpu_load15");
		v.add("mem_swpd");
		v.add("mem_free");
		v.add("mem_buff");
		v.add("mem_cache");
		// BlobSeer provider parameters
		v.add("read_ops");
		v.add("write_ops");
		v.add("free_space");
		v.add("pages_in");
		v.add("pages_out");
		//v.add("vector_sizes");
		v.add("provider_alive");
		return v;

	}

	// ---------------------------------------------

	@SuppressWarnings("unchecked")
	public Vector<GValue> getValues(String param) {

		Vector<GValue> v = new Vector<GValue>();
		GValue cV = new GValue();
		cV.sName = param;

		if (!checkProviderAlive()) {
			//System.out.println("THE PROVIDER IS DEAD!!!");
			return v;
		}

		//System.out.println("The provider is ALIVE");
		processLogFile();

		if (param.equals("read_ops")) {

			v = (Vector<GValue>)readLogs.clone();
			readLogs.removeAllElements();

		} else if (param.equals("write_ops")) {

			v = (Vector<GValue>)writeLogs.clone();
			writeLogs.removeAllElements();

		} else if (param.equals("free_space")) {

			v = (Vector<GValue>)spaceLogs.clone();
			spaceLogs.removeAllElements();

		} else if (param.equals("pages_in")) {

			v = (Vector<GValue>)inLogs.clone();
			inLogs.removeAllElements();

		} else if (param.equals("pages_out")) {

			v = (Vector<GValue>)inLogs.clone();
			outLogs.removeAllElements();

		} else if (param.equals("vector_sizes")) {

			v = new Vector<GValue>();

			cV = new GValue();
			cV.sInfo = "readLogs";
			cV.sValue = (double)readLogs.size();
			v.add(cV);
			cV = new GValue();
			cV.sInfo = "writeLogs";
			cV.sValue = (double)writeLogs.size();
			v.add(cV);

		} else if (param.equals("provider_alive")) {

			v = new Vector<GValue>();
			cV = new GValue();
			cV.sValue = 1.0;
			v.add(cV);

		} else if (param.equals("cpu_load1")) {

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

		} else if (param.equals("mem_swpd")) {

			Vector<Double> vals = readMemValues();
			cV.sValue = ((Double) vals.elementAt(0)).doubleValue();
			cV.sUnits = "kB";
			v.add(cV);

		} else if (param.equals("mem_free")) {

			Vector<Double> vals = readMemValues();
			cV.sValue = ((Double) vals.elementAt(1)).doubleValue();
			cV.sUnits = "kB";
			v.add(cV);

		} else if (param.equals("mem_buff")) {

			Vector<Double> vals = readMemValues();
			cV.sValue = ((Double) vals.elementAt(2)).doubleValue();
			cV.sUnits = "kB";
			v.add(cV);

		} else if (param.equals("mem_cache")) {

			Vector<Double> vals = readMemValues();
			cV.sValue = ((Double) vals.elementAt(3)).doubleValue();
			cV.sUnits = "kB";
			v.add(cV);

		}

		return v;
	}

	// ---------------------------------------------
	// Auxilary methods
	// ---------------------------------------------

	private BufferedReader openLogFile(String fileName) {

		BufferedReader bf = null;

		try {
			bf = new BufferedReader (new FileReader (fileName));
		} catch (FileNotFoundException e) {
			System.out.println("BlobSeerProviderPlugin: WARNING. Unable to find "+
					"log file "+fileName+".");
		}

		//goToEnd(bf);

		return bf;

	}

	// ---------------------------------------------

	private void goToEnd(BufferedReader bf) {

		//String s;

		try {
			while (bf.ready())
				bf.readLine();
		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	// ---------------------------------------------

	private void processLogFile() {

		try {
			if (!logBuffer.ready()) {
				logBuffer = openLogFile(logFile);
				goToEnd(logBuffer);
			}
			while (logBuffer.ready()) {

				String line = logBuffer.readLine();

				if (checkLine(line)) {
					GValue info = parseLogLine(line);
					// Adding to the correspondant log vector
					if (info.sInfo.equals("RPS")) {
						readLogs.add(info);
						outLogs.add(info);
					} else if (info.sInfo.equals("WPS")) {
						writeLogs.add(info);
						inLogs.add(info);
					} else if (info.sInfo.equals("FSC")) {
						spaceLogs.add(info);
					}
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	// ---------------------------------------------

	private boolean checkLine(String line) {

		//String result = null;
		String logLinePattern = "\\[INFO\\s.*\\].*\\(\\w\\w\\w\\)$";
		Pattern pattern = Pattern.compile(logLinePattern);
		Matcher matcher = pattern.matcher(line);
		boolean matchFound = matcher.matches();

		return matchFound;
	}

	// ---------------------------------------------

	private GValue parseLogLine(String line) {

		GValue info = new GValue();

		info.sTime = getTimeStamp(line).getTime();
		info.sValue = Double.parseDouble(getValue(line));
		info.sInfo = getCommand(line);

		return info;

	}

	// ---------------------------------------------

	private Date getTimeStamp(String line) {

		String resultStr = null;
		Date result = null;
		String commandPattern = "^\\[INFO\\s[^\\[\\]]*\\]";
		Pattern pattern = Pattern.compile(commandPattern);
		Matcher matcher = pattern.matcher(line);
		boolean matchFound = matcher.find();

		if (matchFound) {
			int start = matcher.start();
			int end = matcher.end();
			// the end is index of the last matching character + 1
			// The +6 and -4 are to skip the '[INFO ', ']' and the last three digits
			resultStr = line.substring(start+6, end-4);
			SimpleDateFormat dateFormat = new SimpleDateFormat();
			dateFormat.applyPattern("yyyy-MMM-dd HH:mm:ss.SSS");
			try {
				result = dateFormat.parse(resultStr);
			} catch (Exception e) {
				e.printStackTrace();
			}
		}

		return result;
	}

	// ---------------------------------------------

	private String getCommand(String line) {

		String result = null;
		String commandPattern = "\\(\\w\\w\\w\\)$";
		Pattern pattern = Pattern.compile(commandPattern);
		Matcher matcher = pattern.matcher(line);
		boolean matchFound = matcher.find();

		if (matchFound) {
			int start = matcher.start();
			int end = matcher.end();
			// the end is index of the last matching character + 1
			// The -1 and +1 are to skip the '(' and ')'
			result = line.substring(start+1, end-1);
		}

		return result;
	}

	// ---------------------------------------------

	private String getValue(String line) {

		String result = null;
		String commandPattern = "\\{[^\\{\\}]*\\}";
		Pattern pattern = Pattern.compile(commandPattern);
		Matcher matcher = pattern.matcher(line);
		boolean matchFound = matcher.find();

		if (matchFound) {
			int start = matcher.start();
			int end = matcher.end();
			// the end is index of the last matching character + 1
			// The -1 and +1 are to skip the '{' and '}'
			result = line.substring(start+1, end-1);
		}

		return result;
	}

	// ---------------------------------------------

	private boolean checkProviderAlive() {

		boolean alive = true;

		try {

			Process child = Runtime.getRuntime().exec("Plugins/check_provider.sh");
			child.waitFor();
			if (child.exitValue() != 0)
				alive = false;

		}  catch (Exception e) {
			e.printStackTrace();
		}

		return alive;

	}

	// ---------------------------------------------

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

	// ---------------------------------------------

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

	// ---------------------------------------------

//	private Vector readLoadValues() {
//
//		return readMonScript("Plugins/readload.sh");
//
//	}

//	private Vector readMemValues() {
//
//		return readMonScript("Plugins/readmem.sh");
//	}

	// ---------------------------------------------

//	private Vector readMonScript(String script) {
//
//		Vector results = new Vector();
//
//		try {
//			Process child = Runtime.getRuntime().exec(script);
//			child.waitFor();
//			BufferedInputStream childOutput = (BufferedInputStream) child.getInputStream();
//			int val = childOutput.read();
//			String value = "";
//			while (val != -1) {
//				char c = (char)val;
//				if ((c != ' ') && (c != '\n'))
//					value = value + c;
//				else {
//					results.add(Double.parseDouble(value));
//					value = "";
//				}
//				val = childOutput.read();
//			}
//		} catch (Exception e) {
//			e.printStackTrace();
//		}
//		//System.out.println("BasicPlugin: "+results);
//		return results;
//	}

	// ---------------------------------------------
	// Testing methods
	// ---------------------------------------------

	public void test() {

		System.out.println("BolbSeerProviderPlugin: Starting test...");

		try {
			while (logBuffer.ready()) {

				String line = logBuffer.readLine();

				if (checkLine(line)) {
					GValue info = parseLogLine(line);
					System.out.println(info.sTime+" : "+info.sInfo+" : "+info.sValue);
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	public static void main(String[] args) {
		BlobSeerProviderPlugin p = new BlobSeerProviderPlugin();
		p.test();
	}

}
