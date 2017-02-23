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

package common;
import java.io.Serializable;

public class GValue implements Serializable {

	private static final long serialVersionUID = 1L;

	public String sName;
	public long sTime;
	public double sValue;
	public String sHost;
	public String sInfo;
	public String sUnits;

	public GValue() {
		super();
		// TODO Auto-generated constructor stub
	}

	public String toString() {
		return "GValue("+sName+","+sTime+","+sValue+","+sHost+","+sInfo+","+sUnits+")";
	}

	public boolean equals(Object obj) {
		GValue value = (GValue) obj;
		return (value.sName.equals(sName) && value.sHost.equals(sHost) && (value.sTime == sTime));
	}
}
