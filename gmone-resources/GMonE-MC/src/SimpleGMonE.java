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

import java.io.BufferedReader;
import java.io.FileReader;
import java.rmi.Naming;
import java.util.Vector;
import common.GValue;
import common.GMonEMonInterface;

public class SimpleGMonE {

	/**
	 * @param args
	 */
	//private String black = "\033[30m";
	//private String magenta = "\033[35m";
	//private String cyan = "\033[36m";
	//private String white = "\033[37m";
	//private String blue = "\033[34m";

	private String red = "\033[31m";
	private String green = "\033[32m";
	private String yellow = "\033[33m";
	private String reset = "\033[0m";
	/*
	private String red = "";
	private String green = "";
	private String yellow = "";
	private String reset = "";
	*/
	private String clear = "\033[2J";
	
	public String generate_bar(double percentage) {

		double yellow_th = 50.0;
		double red_th = 75.0;
		
		String color = green;
		
		if (percentage >= red_th) {
			color = red;
		} else if (percentage >= yellow_th) {
			color = yellow;
		}
		
		String bar = "["+color;

		double count = 0.0;

		while (count < percentage) {
			bar = bar + "=";
			count = count + 5.0;
		}
		while (count < 100.0) {
			bar = bar + " ";
			count = count + 5.0;
		}
		bar = bar + reset +"]";

		return bar;
	}

	public String percent_str(double percentage) {
		
		String res = "";
		
		if (percentage < 10.0) {
			res = "  ";
		} else if (percentage < 100.0) {
			res = " ";
		}
		
		return res+(int)(percentage)+"%";
	}
	
	public static void main(String[] args) {
		// Comprobando que el número de argumentos es correcto.
		if (args.length != 2) {
			System.err.println("args: <bars|full> <host file>");
			System.exit(1);
		}

		Vector<String> hosts = new Vector<String>();

		try {
			FileReader fr = new FileReader(args[1]);
			BufferedReader br = new BufferedReader(fr);
			while (br.ready()){
				// Loading host names
				String host = br.readLine();
				hosts.add(host);
			}

			String mode = args[0];
			
			if (mode.equals("bars")) {

				SimpleGMonE obj = new SimpleGMonE();

				Vector<String> lines = new Vector<String>();
				// Leyendo datos de cada host
				for (int h=0; h < hosts.size(); h++) {
					String host = hosts.elementAt(h);
					
					try {
						// Conectándose al GMonEMon
						GMonEMonInterface m = (GMonEMonInterface) Naming.lookup("//"+host+":10990/GMonEMon");

						// Obteniendo datos de CPU
						Vector<GValue> values = m.consult("cpu_usage");
						GValue last_val = values.elementAt(values.size()-1);
						double cpu_usage = last_val.sValue;

						// Obteniendo datos de memoria
						values = m.consult("mem_usage");
						last_val = values.elementAt(values.size()-1);
						double mem_usage = last_val.sValue;

						// Obteniendo datos de carga
						values = m.consult("cpu_load1");
						last_val = values.elementAt(values.size()-1);
						double cpu_load = last_val.sValue;

						lines.add(host+":");
						lines.add("CPU "+obj.generate_bar(cpu_usage)+" "+obj.percent_str(cpu_usage)+
								"\t"+"MEM "+obj.generate_bar(mem_usage)+" "+obj.percent_str(mem_usage)+
								"\t"+"LOAD "+cpu_load);
						/*
						System.out.println(host+":");
						System.out.println("CPU "+obj.generate_bar(cpu_usage)+" "+obj.percent_str(cpu_usage)+"\t"+"MEM "+obj.generate_bar(mem_usage)+" "+obj.percent_str(mem_usage)+"\t"+"LOAD "+cpu_load);
						 */
					} catch (Exception uhe) {
						lines.add(host+":\nnot found");
					}
					
				}
				System.out.print(obj.clear);
				System.out.flush();
				for (int i = 0; i < lines.size(); i++) {
					System.out.println(lines.elementAt(i));
				}
				
			} else if (mode.equals("full")) {
				// Leyendo datos de cada host
				for (int h=0; h < hosts.size(); h++) {
					String host = hosts.elementAt(h);
					// Conectándose al GMonEMon
					try {
						GMonEMonInterface m = (GMonEMonInterface) Naming.lookup("//"+host+":10990/GMonEMon");
						System.out.println(host);

						// Obteniendo parámetros
						Vector<String> params = m.getParamList();

						// Consultando parámetos
						for (int i=0; i < params.size(); i++) {
							String par = params.elementAt(i);
							Vector<GValue> values = m.consult(par);
							GValue last_val = values.elementAt(values.size()-1);
							System.out.println("\t"+par+"\t"+last_val.sValue);
						}
					} catch (Exception uhe) {
						System.out.println(host+" not found");
					}

				}
			} else {
				System.out.println("Mode "+mode+" unknown");
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

	}

}
