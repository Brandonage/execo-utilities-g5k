package gmonemon.plugin;

/**
 * Created by alvarobrandon on 25/04/16.
 */

import java.util.*;
import java.io.*;
import common.*;

public class DStatPlugin implements GMonEMonPluginInterface {

    public DStatPlugin() {
    }

    public Vector<String> getParams(){
        Vector<String> v = new Vector<String>();
        v.add("cpu_usr");
        v.add("cpu_sys");
        v.add("cpu_idl");
        v.add("cpu_wait");
        v.add("cpu_hiq");
        v.add("cpu_siq");
        v.add("disk_read");
        v.add("disk_write");
        v.add("net_recv");
        v.add("net_send");
        v.add("paging_in");
        v.add("paging_out");
        v.add("sys_interrupts");
        v.add("sys_contswitch");
//        v.add("mem_used");
//        v.add("mem_buffer");
//        v.add("mem_cached");
//        v.add("mem_free");
        v.add("procs_run");
        v.add("procs_blk");
        v.add("procs_new");
        v.add("io_total_read");
        v.add("io_total_write");
//        v.add("sysv_ipc_msg");
//        v.add("sysv_ipc_sem");
//        v.add("sysv_ipc_shm");
//        v.add("sockets_tot");
//        v.add("sockets_tcp");
//        v.add("sockets_udp");
//        v.add("sockets_raw");
//        v.add("sockets_frq");
        v.add("pkt_total_recv");
        v.add("pkt_total_send");
        v.add("proc");
        v.add("disk_percentage");
//        v.add("rpc_client_call");
//        v.add("rpc_client_retr");
//        v.add("rpc_client_refr");
//        v.add("rpc_server_call");
//        v.add("rpc_server_erca");
//        v.add("rpc_server_erau");
//        v.add("rpc_server_call_erc1");
//        v.add("rpc_server_call_xdrc");
//        v.add("virtual_mem_majpf");
//        v.add("virtual_mem_minpf");
//        v.add("virtual_mem_alloc");
//        v.add("virtual_mem_free");
        return v;
    }

    public Vector<GValue> getValues(String param) {
        Vector<GValue> v = new Vector<GValue>();
        GValue cV = new GValue();
        cV.sName = param;
        Vector<Double> vals = readDstatValues();
        if (param.equals("cpu_usr")) {
            cV.sValue = ((Double) vals.elementAt(0)).doubleValue();
            cV.sUnits = "%";
            v.add(cV);
        }
        else if (param.equals("cpu_sys")) {
            cV.sValue = ((Double) vals.elementAt(1)).doubleValue();
            cV.sUnits = "%";
            v.add(cV);
        }
        else if (param.equals("cpu_idl")) {
            cV.sValue = ((Double) vals.elementAt(2)).doubleValue();
            cV.sUnits = "%";
            v.add(cV);
        }
        else if (param.equals("cpu_wait")) {
            cV.sValue = ((Double) vals.elementAt(3)).doubleValue();
            cV.sUnits = "%";
            v.add(cV);
        }
        else if (param.equals("cpu_hiq")) {
            cV.sValue = ((Double) vals.elementAt(4)).doubleValue();
            cV.sUnits = "%";
            v.add(cV);
        }
        else if (param.equals("cpu_siq")) {
            cV.sValue = ((Double) vals.elementAt(5)).doubleValue();
            cV.sUnits = "%";
            v.add(cV);
        }
        else if (param.equals("disk_read")) {
            cV.sValue = ((Double) vals.elementAt(6)).doubleValue();
            cV.sUnits = "Bytes";
            v.add(cV);
        }
        else if (param.equals("disk_write")) {
            cV.sValue = ((Double) vals.elementAt(7)).doubleValue();
            cV.sUnits = "Bytes";
            v.add(cV);
        }
        else if (param.equals("net_recv")) {
            cV.sValue = ((Double) vals.elementAt(8)).doubleValue();
            cV.sUnits = "Bytes";
            v.add(cV);
        }
        else if (param.equals("net_send")) {
            cV.sValue = ((Double) vals.elementAt(9)).doubleValue();
            cV.sUnits = "Bytes";
            v.add(cV);
        }
        else if (param.equals("paging_in")) {
            cV.sValue = ((Double) vals.elementAt(10)).doubleValue();
            cV.sUnits = "Bytes";
            v.add(cV);
        }
        else if (param.equals("paging_out")) {
            cV.sValue = ((Double) vals.elementAt(11)).doubleValue();
            cV.sUnits = "Bytes";
            v.add(cV);
        }
        else if (param.equals("sys_interrupts")) {
            cV.sValue = ((Double) vals.elementAt(12)).doubleValue();
            v.add(cV);
        }
        else if (param.equals("sys_contswitch")) {
            cV.sValue = ((Double) vals.elementAt(13)).doubleValue();
            v.add(cV);
        }
//        else if (param.equals("mem_used")) {
//            cV.sValue = ((Double) vals.elementAt(14)).doubleValue();
//            cV.sUnits = "Bytes";
//            v.add(cV);
//        }
//        else if (param.equals("mem_buffer")) {
//            cV.sValue = ((Double) vals.elementAt(15)).doubleValue();
//            cV.sUnits = "Bytes";
//            v.add(cV);
//        }
//        else if (param.equals("mem_cached")) {
//            cV.sValue = ((Double) vals.elementAt(16)).doubleValue();
//            cV.sUnits = "Bytes";
//            v.add(cV);
//        }
//        else if (param.equals("mem_free")) {
//            cV.sValue = ((Double) vals.elementAt(17)).doubleValue();
//            cV.sUnits = "Bytes";
//            v.add(cV);
//        }
        else if (param.equals("procs_run")) {
            cV.sValue = ((Double) vals.elementAt(18)).doubleValue();
            cV.sUnits = "Num";
            v.add(cV);
        }
        else if (param.equals("procs_blk")) {
            cV.sValue = ((Double) vals.elementAt(19)).doubleValue();
            cV.sUnits = "Num";
            v.add(cV);
        }
        else if (param.equals("procs_new")) {
            cV.sValue = ((Double) vals.elementAt(20)).doubleValue();
            cV.sUnits = "Num";
            v.add(cV);
        }
        else if (param.equals("io_total_read")) {
            cV.sValue = ((Double) vals.elementAt(21)).doubleValue();
            cV.sUnits = "Operations";
            v.add(cV);
        }
        else if (param.equals("io_total_write")) {
            cV.sValue = ((Double) vals.elementAt(22)).doubleValue();
            cV.sUnits = "Operations";
            v.add(cV);
        }
//        else if (param.equals("sysv_ipc_msg")) {
//            cV.sValue = ((Double) vals.elementAt(23)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("sysv_ipc_sem")) {
//            cV.sValue = ((Double) vals.elementAt(24)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("sysv_ipc_shm")) {
//            cV.sValue = ((Double) vals.elementAt(25)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("sockets_tot")) {
//            cV.sValue = ((Double) vals.elementAt(26)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("sockets_tcp")) {
//            cV.sValue = ((Double) vals.elementAt(27)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("sockets_udp")) {
//            cV.sValue = ((Double) vals.elementAt(28)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("sockets_raw")) {
//            cV.sValue = ((Double) vals.elementAt(29)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("sockets_frq")) {
//            cV.sValue = ((Double) vals.elementAt(30)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
        else if (param.equals("pkt_total_recv")) {
            cV.sValue = ((Double) vals.elementAt(31)).doubleValue();
            cV.sUnits = "Num";
            v.add(cV);
        }
        else if (param.equals("pkt_total_send")) {
            cV.sValue = ((Double) vals.elementAt(32)).doubleValue();
            cV.sUnits = "Num";
            v.add(cV);
        }
        else if (param.equals("proc")) {
            cV.sValue = ((Double) vals.elementAt(33)).doubleValue();
            cV.sUnits = "Num";
            v.add(cV);
        }
        else if (param.equals("disk_percentage")) {
            cV.sValue = ((Double) vals.elementAt(34)).doubleValue();
            cV.sUnits = "%";
            v.add(cV);
        }
//        else if (param.equals("rpc_client_call")) {
//            cV.sValue = ((Double) vals.elementAt(35)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("rpc_client_retr")) {
//            cV.sValue = ((Double) vals.elementAt(36)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("rpc_client_refr")) {
//            cV.sValue = ((Double) vals.elementAt(37)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("rpc_server_call")) {
//            cV.sValue = ((Double) vals.elementAt(38)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("rpc_server_erca")) {
//            cV.sValue = ((Double) vals.elementAt(39)).doubleValue();
//            cV.sUnits = "Bytes";
//            v.add(cV);
//        }
//        else if (param.equals("rpc_server_erau")) {
//            cV.sValue = ((Double) vals.elementAt(40)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("rpc_server_call_erc1")) {
//            cV.sValue = ((Double) vals.elementAt(41)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("rpc_server_call_xdrc")) {
//            cV.sValue = ((Double) vals.elementAt(42)).doubleValue();
//            cV.sUnits = "Num";
//            v.add(cV);
//        }
//        else if (param.equals("virtual_mem_majpf")) {
//            cV.sValue = ((Double) vals.elementAt(43)).doubleValue();
//            cV.sUnits = "Bytes";
//            v.add(cV);
//        }
//        else if (param.equals("virtual_mem_minpf")) {
//            cV.sValue = ((Double) vals.elementAt(44)).doubleValue();
//            cV.sUnits = "Bytes";
//            v.add(cV);
//        }
//        else if (param.equals("virtual_mem_alloc")) {
//            cV.sValue = ((Double) vals.elementAt(45)).doubleValue();
//            cV.sUnits = "Bytes";
//            v.add(cV);
//        }
//        else if (param.equals("virtual_mem_free")) {
//            cV.sValue = ((Double) vals.elementAt(46)).doubleValue();
//            cV.sUnits = "Bytes";
//            v.add(cV);
//        }
        return v;

    }

    private Vector<Double> readDstatValues(){
        Vector<Double> results = new Vector<Double>();
        try {
            Process child = Runtime.getRuntime().exec("./dstat_last_line.sh"); //It tails the following file: "tail -1 /opt/GMonE-MC/dstat.csv"
            child.waitFor();
            BufferedReader stdOutput = new BufferedReader(new
                    InputStreamReader(child.getInputStream()));
            String line = stdOutput.readLine();
            String[] tokens = line.split(",");
            for (int i=0; i<tokens.length ; i++){
                results.add(Double.parseDouble(tokens[i]));
            }
            return results;

        } catch (Exception e) {
            e.printStackTrace();
            String [] tokens = new String[47];
            for (int i=0; i<tokens.length ; i++){
                results.add(Double.parseDouble(tokens[i]));
            }
            return results;
            }

    }

    public void test(){
        GMonELogger.message("Reading dstat values...");
        GMonELogger.message("LOAD: "+this.readDstatValues());
        GMonELogger.message(this.getValues("cpu_usr").toString());
        GMonELogger.message(this.getValues("cpu_sys").toString());
        GMonELogger.message(this.getValues("cpu_idl").toString());
        GMonELogger.message(this.getValues("cpu_wait").toString());
        GMonELogger.message(this.getValues("cpu_hiq").toString());
        GMonELogger.message(this.getValues("cpu_siq").toString());
        GMonELogger.message(this.getValues("disk_read").toString());
        GMonELogger.message(this.getValues("disk_write").toString());
        GMonELogger.message(this.getValues("net_recv").toString());
        GMonELogger.message(this.getValues("net_send").toString());
        GMonELogger.message(this.getValues("paging_in").toString());
        GMonELogger.message(this.getValues("paging_out").toString());
        GMonELogger.message(this.getValues("sys_interrupts").toString());
        GMonELogger.message(this.getValues("sys_contswitch").toString());
        GMonELogger.message(this.getValues("sys_contswitch").toString());
        GMonELogger.message(this.getValues("mem_used").toString());
        GMonELogger.message(this.getValues("mem_buffer").toString());
        GMonELogger.message(this.getValues("mem_cached").toString());
        GMonELogger.message(this.getValues("mem_free").toString());
        GMonELogger.message(this.getValues("procs_run").toString());
        GMonELogger.message(this.getValues("procs_blk").toString());
        GMonELogger.message(this.getValues("procs_new").toString());
        GMonELogger.message(this.getValues("io_total_read").toString());
        GMonELogger.message(this.getValues("io_total_write").toString());
        GMonELogger.message(this.getValues("sysv_ipc_msg").toString());
        GMonELogger.message(this.getValues("sysv_ipc_sem").toString());
        GMonELogger.message(this.getValues("sysv_ipc_shm").toString());
        GMonELogger.message(this.getValues("sockets_tot").toString());
        GMonELogger.message(this.getValues("sockets_tcp").toString());
        GMonELogger.message(this.getValues("sockets_udp").toString());
        GMonELogger.message(this.getValues("sockets_raw").toString());
        GMonELogger.message(this.getValues("sockets_frq").toString());
        GMonELogger.message(this.getValues("pkt_total_recv").toString());
        GMonELogger.message(this.getValues("pkt_total_send").toString());
        GMonELogger.message(this.getValues("proc").toString());
        GMonELogger.message(this.getValues("disk_percentage").toString());
        GMonELogger.message(this.getValues("rpc_client_call").toString());
        GMonELogger.message(this.getValues("rpc_client_retr").toString());
        GMonELogger.message(this.getValues("rpc_client_refr").toString());
        GMonELogger.message(this.getValues("rpc_server_call").toString());
        GMonELogger.message(this.getValues("rpc_server_erca").toString());
        GMonELogger.message(this.getValues("rpc_server_erau").toString());
        GMonELogger.message(this.getValues("rpc_server_call_erc1").toString());
        GMonELogger.message(this.getValues("rpc_server_call_xdrc").toString());
        GMonELogger.message(this.getValues("virtual_mem_majpf").toString());
        GMonELogger.message(this.getValues("virtual_mem_minpf").toString());
        GMonELogger.message(this.getValues("virtual_mem_alloc").toString());
        GMonELogger.message(this.getValues("virtual_mem_free").toString());
        GMonELogger.message("Values read...");
    }

    public static void main(String[] args) {
        DStatPlugin p = new DStatPlugin();
        p.test();
    }

}
