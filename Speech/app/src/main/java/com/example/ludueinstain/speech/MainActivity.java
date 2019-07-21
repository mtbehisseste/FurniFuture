package com.example.ludueinstain.speech;

import android.annotation.TargetApi;
import android.app.Service;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.os.Build;
import android.os.Handler;
import android.os.StrictMode;
import android.os.Vibrator;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.support.annotation.RequiresApi;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.method.ScrollingMovementMethod;
import android.util.Log;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;
import java.util.ArrayList;
import java.util.Locale;

import itri.org.record.ITRIAudioRecorder;

public class MainActivity extends AppCompatActivity {
    private EditText txtSpeechInput;
    private TextView textview;
    private Button button2;
    private Thread t;
    private String host;
    private String port;
    ITRIAudioRecorder ItriRecord;

//    ITRI stt
    private static final boolean DBG = true;
    private static final String TAG = "SSTSample";
    String AuthorizationID = "";
    String locName = "";
    String taskName = "";
    int rate = 0;
    Boolean recordStatus = false;

    public MainActivity(){
        AuthorizationID = "211dae7f02d61d723114709ca1c1d917";
        locName = "useUserDefineSTT";
        taskName = "Check";
        rate = 16000;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (android.os.Build.VERSION.SDK_INT > 9) {
            StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
            StrictMode.setThreadPolicy(policy);
        }
        txtSpeechInput = findViewById(R.id.txtSpeechInput);
        textview = findViewById(R.id.textView);

        Intent intent = getIntent();
        host = intent.getStringExtra("EXTRA_IP");
        port = intent.getStringExtra("EXTRA_PORT");
        System.out.println(host + port);

        /* socket */
        try {
            t = new Thread(readData);
            t.start();
        } catch (Exception e) {
            Log.i("Client_Socket", e.getMessage());
        }

        /* itri stt */
        recordInit();

        /* tts */
        createLanguageTTS();
    }

    /*******************
     * socket
     *******************/
    Socket clientSocket;
    public static Handler mHandler = new Handler();

    /* receive from server */
    private StringBuffer temp = new StringBuffer();
    private String result;

    private Runnable readData = new Runnable() {
        public void run() {
            try {
                clientSocket = new Socket();
                SocketAddress hostPort = new InetSocketAddress(host, Integer.parseInt(port));
                clientSocket.connect(hostPort, 5000);
                Log.i("Client_Socket", "Connected Successfully!");

                while (clientSocket.isConnected()) {
                    DataInputStream inputData = new DataInputStream(clientSocket.getInputStream());  // receive from server
                    InputStreamReader isr = new InputStreamReader(inputData, "UTF-8");

                    int count = 0;
                    char[] buf = new char[1024*64];
                    while((count = isr.read(buf, 0, buf.length)) > -1){  // -1 stands for end of stream
                        temp.append(buf, 0, count);
                        if (count < 1024*64)
                            break;
                    }
                    result = temp.toString();

                    if(temp.charAt(temp.length()-1) == '\n') {
                        Log.i("Client_Socket", "Server: " + temp.toString());

                        //result = new String(temp.toString().getBytes(), "UTF-8");

                        mHandler.post(updateText);
                    }
                }
            } catch (Exception e) {
                System.out.println("Exception: " + e.getMessage());
                e.printStackTrace();

                /* show error message */
                runOnUiThread(new Runnable() {
                    public void run() {
                        Toast toast = Toast.makeText(MainActivity.this, "Host or Port Not Found !!", Toast.LENGTH_SHORT);
                        toast.setGravity(Gravity.CENTER_VERTICAL| Gravity.CENTER_HORIZONTAL, 0, 0);
                        toast.show();
                    }
                });

                /* wrong host or port, return to last intent */
                Intent intent = new Intent(MainActivity.this, Welcome.class);
                startActivity(intent);
            }
        }
    };

    private Runnable updateText = new Runnable() {
        public void run() {
            textview.setMovementMethod(ScrollingMovementMethod.getInstance());  // for scrolling server message
            textview.append("Server: " + result + "\n");

            transfer(result);  // tts transfer

            temp.setLength(0);  // reset string buffer
            txtSpeechInput.setText("");
        }
    };

    /* send to server */
    private void sentToServer(String s) {
        if(clientSocket.isConnected()) {
            BufferedWriter bw;
            try {
                bw = new BufferedWriter(new OutputStreamWriter(clientSocket.getOutputStream(), "utf-8"));
                bw.write(s);  // string to send to python server

                bw.flush();
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    /********************
     * speech to text
     ********************/
    /* OnRecorderListener function */
    public ITRIAudioRecorder.OnRecorderListener recorderListener = new ITRIAudioRecorder.OnRecorderListener() {
        @Override
        public void onStartRecord() {
            /*if (DBG)
                Log.e(TAG, "main onStartRecord");

           sttResult.setText("辨識中..."); */
        }

        @Override
        public void onStopRecord() {
            if (DBG)
                Log.e(TAG, "main onStopRecord");

            //if(sttResult.getText().toString() != "無語音輸入!!" && recordStatus != true)
            //    sttResult.setText("手動中斷辨識!!");

            recordStatus = false;

            ItriRecord.stopRecord();
        }

        @Override
        public void onVadNoVoice() {
            if (DBG)
                Log.e(TAG, "main onVadNoVoice");

            ItriRecord.stopRecord();
        }

        @Override
        public void onErr(int errCode, String errMsg) {
            if (DBG)
                Log.e(TAG, "RECORD_ERROR!errcode: " + errCode + " errMsg: " + errMsg);
        }

        @Override
        public void onVolume(double db) {
            // Log.e(TAG, "onVolume:"+db);
        }

        @Override
        public void onSTTResult(String jsonResult) {
                try {
                    JSONObject jsonObject = new JSONObject(jsonResult);
                    int sttStatus = jsonObject.getInt("status");
                    String sents = jsonObject.getJSONArray("sents").getJSONObject(0).getString("sent");

                    txtSpeechInput.setText(sents);
                    sentToServer(sents);
                    textview.append("You said: " + sents + "\n\n");
                }
                catch (JSONException e) {
                    e.printStackTrace();
                }
        }

        public void onRecordPart(short[] buffer, String otherParams, int states) {
            if (DBG)
                Log.e(TAG, "buffer length:" + buffer.length);

            int simplerate = 16000;

            if (DBG)
                Log.e(TAG, "states:" + states + " buffer length:" + buffer.length);
        }
    };

//    private final int REQ_CODE_SPEECH_INPUT = 100;
//
//    /* Showing google speech input dialog */
//    public void promptSpeechInputNotView() {
//        Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
//        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
//        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.CHINESE);
//        intent.putExtra(RecognizerIntent.EXTRA_PROMPT, getString(R.string.speech_prompt));
//        try {
//            startActivityForResult(intent, REQ_CODE_SPEECH_INPUT);
//        } catch (ActivityNotFoundException a) {
//            Toast.makeText(getApplicationContext(),
//                    getString(R.string.speech_not_supported),
//                    Toast.LENGTH_SHORT).show();
//        }
//    }
//
//    /* Receiving speech input */
//    @Override
//    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
//        super.onActivityResult(requestCode, resultCode, data);
//
//        switch (requestCode) {
//            case REQ_CODE_SPEECH_INPUT: {
//                if (resultCode == RESULT_OK && null != data && clientSocket != null) {
//                    ArrayList<String> result = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
//                    if (result.size() > 0) {
//                        String tmpresult = result.get(0);
//                        txtSpeechInput.setText(tmpresult);
//                        System.out.println(tmpresult);
//
//                        sentToServer(tmpresult);
//                        textview.append("You said: " + tmpresult + "\n\n");
//                    } else {  // no recognizable input
//                        System.out.println("stopped");
//                        finish();
//                    }
//                }
//
//                break;
//            }
//        }
//    }

    /* click button to confirm input text */
    public void confirm_input(View view) {
        String input = txtSpeechInput.getText().toString();
        sentToServer(input);
        textview.append("You said: " + input + "\n\n");
        txtSpeechInput.setText("");
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    private void recordInit(){
        ItriRecord = new ITRIAudioRecorder();
        ItriRecord.setOnRecorderListener(recorderListener);
        ItriRecord.setSTTVariable(AuthorizationID, locName, taskName, rate);
    }

    @TargetApi(Build.VERSION_CODES.O)
    @RequiresApi(api = Build.VERSION_CODES.LOLLIPOP)
    @Override
    public boolean onKeyLongPress(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_VOLUME_DOWN || keyCode == KeyEvent.KEYCODE_VOLUME_UP) {
            /*** for API level 26
             Vibrator vibrator = (Vibrator) getApplication().getSystemService(Service.VIBRATOR_SERVICE);
             VibrationEffect vibe = VibrationEffect.createOneShot(100, VibrationEffect.DEFAULT_AMPLITUDE);
             vibrator.vibrate(vibe);
             */
            Vibrator vibrator = (Vibrator) getApplication().getSystemService(Service.VIBRATOR_SERVICE);
            vibrator.vibrate(100);

//            promptSpeechInputNotView();
            recordStatus = true;
            ItriRecord.startRecord("", false);

            return true;
        }
        return true;
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (event.getAction() == KeyEvent.ACTION_DOWN && keyCode == KeyEvent.KEYCODE_VOLUME_DOWN || keyCode == KeyEvent.KEYCODE_VOLUME_UP) {
            event.startTracking();  //tracking button event time
        }

        return true;
    }


    /********************
     * text to speech
     ********************/
    private TextToSpeech tts;

    public void createLanguageTTS() {
        if (tts == null) {
            tts = new TextToSpeech(this, new TextToSpeech.OnInitListener() {
                @Override
                public void onInit(int arg0) {
                if (arg0 == TextToSpeech.SUCCESS) {
                    //language
                    Locale lan = Locale.CHINESE;

                    if (tts.isLanguageAvailable(lan) == TextToSpeech.LANG_COUNTRY_AVAILABLE) {
                        System.out.println("Language " + lan.toString() + " selected.");
                        tts.setLanguage(lan);
                    }
                }
                }
            });
        }
    }

    public void transfer(String s) {
        tts.speak(s, TextToSpeech.QUEUE_FLUSH, null);

        while(tts.isSpeaking()) {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}