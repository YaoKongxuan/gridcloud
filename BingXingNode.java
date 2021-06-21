package com.cloud;

import org.json.JSONException;
import org.json.JSONObject;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.SocketException;
import java.util.HashMap;
import java.util.Map;

public class BingXingNode {
    public static void main(String[] args) {
        // 发送socket程序
        DatagramSocket socketsend = null;
        try {
            socketsend = new DatagramSocket();
        } catch (SocketException e) {

            e.printStackTrace();
        }
        // 接收socket程序
        DatagramSocket socketrec = null;
        try {
            socketrec = new DatagramSocket(50100);
        } catch (SocketException e) {
            e.printStackTrace();
        }
        // 接收socket程序
        DatagramSocket socketrectwo = null;
        try {
            socketrectwo = new DatagramSocket(50200);
            socketrectwo.setSoTimeout(1000); // 设置阻塞时间
        } catch (SocketException e) {
            e.printStackTrace();
        }
        while(true){
            //接收数据包
            //接收超时就重新发送这个数据的
            byte[] arr = new byte[1024];
            DatagramPacket packetrec = new DatagramPacket(arr, arr.length);
            try {
                socketrec.receive(packetrec);
            } catch (IOException e) {
                System.out.println("未接收到信息超时");
                continue;
            }
            System.out.println("收到任务开始处理");
            //第一次发送
            DatagramPacket packetsend = null;
            byte[] arr1 = packetrec.getData();
            String res = new String(arr1).trim();
            JSONObject resjson = null;
            try {
                resjson = new JSONObject(res);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            String re = "ok";
            byte[] reby = re.getBytes();
            try {
                try {
                    packetsend = new DatagramPacket
                            (reby, reby.length, packetrec.getAddress() , resjson.getInt("port"));
                    System.out.println(resjson.getInt("port"));
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                socketsend.send(packetsend);
            } catch (IOException e) {
                e.printStackTrace();
            }
            //接收数据包
            //接收超时就重新发送这个数据的
            arr = new byte[1024];
            packetrec = new DatagramPacket(arr, arr.length);
            try {
                socketrectwo.receive(packetrec);
            } catch (IOException e) {
                System.out.println(res);
                System.out.println("没有抢到该任务");
                continue;
            }
            System.out.println(res);
            System.out.println("抢到任务开始计算");
            arr1 = packetrec.getData();
            res = new String(arr1).trim();
            resjson = null;
            try {
                resjson = new JSONObject(res);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            int resans = 0;
            int row = 0,col = 0;
            String row_data = null,col_data = null;
            try {
                row = resjson.getInt("row");
                col = resjson.getInt("col");
                row_data = resjson.getString("row_data");
                col_data = resjson.getString("col_data");
            } catch (JSONException e) {
                e.printStackTrace();
            }
            String row_datas[] = row_data.split(" ");
            String col_datas[] = col_data.split(" ");
            for(int i = 0;i<row_datas.length;i++)
            {
                resans+=Double.parseDouble(row_datas[i])*Double.parseDouble(col_datas[i]);
            }
            Map<String, String> map = new HashMap<>();
            map.put("res",String.valueOf(resans));
            map.put("row",String.valueOf(row));
            map.put("col",String.valueOf(col));
            //将json转化为String类型
            JSONObject json = new JSONObject(map);
            String jsonString = "";
            jsonString = json.toString();
            //将String转化为byte[]
            byte[] jsonByte = jsonString.getBytes();
            try {
                try {
                    packetsend = new DatagramPacket
                            (jsonByte, jsonByte.length, packetrec.getAddress() , resjson.getInt("port"));
                    System.out.println(resjson.getInt("port"));
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                socketsend.send(packetsend);
            } catch (IOException e) {
                e.printStackTrace();
            }
            System.out.println("本次任务结束");
        }
    }
}
