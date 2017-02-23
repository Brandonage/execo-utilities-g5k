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

import java.rmi.Naming;
import java.util.Vector;
import common.*;

public class SampleClient {

    public SampleClient() {
    	super();
    }

    public static void main(String[] args) {

    	// Comprobando que el número de argumentos es correcto.
    	if (args.length != 2) {
    		System.err.println("args: <GMonEDB host> <minutos>");
    		System.exit(1);
    	}
    	
    	try {
    		// Conectándose al GMonEDB
    		GMonEAccessInterface m = (GMonEAccessInterface) Naming.lookup("//"+args[0]+":10990/GMonEAccess");
    		int minutos = Integer.parseInt(args[1]);
    		
    		// Obteniendo la lista de máquinas monitorizadas
    		System.out.println("Obteniendo la lista de máquinas monitorizadas...");
    		Vector<String> hosts = m.getHosts();
    		
    		// Imprimiendo la lista por pantalla
    		for (int i=0; i < hosts.size(); i++) {
    			System.out.println("\t"+hosts.elementAt(i));
    		}
    		
    		// Obteniendo la lista de parámetros monitorizados
    		System.out.println("Obteniendo la lista de parámetros monitorizados...");
    		Vector<String> params = m.getParams();

    		// Imprimiendo la lista por pantalla
    		for (int i=0; i < params.size(); i++) {
    			System.out.println("\t"+params.elementAt(i));
    		}

    		// Obteniendo los valores globales de los útimos 'minutos' minutos para cada uno de los parámetros monitorizados
    		for (int i=0; i< params.size(); i++) {
    			// Leyendo nombre del parámetro
    			String param = params.elementAt(i);
    			long tiempo = 60000*minutos; // 'minutos' minutos en milisegundos
    			System.out.println("Obteniendo valores de '"+param+"' en los últimos "+minutos+" minutos...");
    			// Solicitando los valores a GMonE
    			Vector<GValue> vals = m.queryGlobal(param, tiempo);
    			// Imprimiendo los valores por pantalla
    			for (int j=0; j < vals.size(); j++) {
    				System.out.println("\t"+vals.elementAt(j));
    			}
    		}
    		
    	} catch (Exception e) {
    		e.printStackTrace();
    	}
    }
}
