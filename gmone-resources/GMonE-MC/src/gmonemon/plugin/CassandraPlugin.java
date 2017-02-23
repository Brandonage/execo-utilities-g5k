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

import java.io.File;
import java.util.Vector;

import common.GMonELogger;
import common.GValue;

public class CassandraPlugin implements GMonEMonPluginInterface {

	private long getFileSize(File file) {
 
        long filesize = 0;

        if (file.isDirectory()) {
        	File[] filelist = file.listFiles();
        	for (int i = 0; i < filelist.length; i++) {
        		filesize += getFileSize(filelist[i]);
        	}
        } else {
        	filesize += file.length();
        }
        return filesize;
    }
	
	@Override
	public Vector<String> getParams() {
		Vector<String> v = new Vector<String>();
		v.add(new String("cassandra_size"));
		return v;
	}

	@Override
	public Vector<GValue> getValues(String param) {
		
		Vector<GValue> result = new Vector<GValue>();
		
		if (param.equals("cassandra_size")) {
			File cassandraFolder = new File("/var/lib/cassandra");
			GValue val = new GValue();
			val.sValue = ((double) getFileSize(cassandraFolder)) / 1024.0;
			val.sInfo = new String("");
			val.sUnits = new String("KB");
			result.add(val);
			GMonELogger.message("CassandraPlugin: "+val.sValue+" KB in "+cassandraFolder);
		}
		
		return result;
	}

}
