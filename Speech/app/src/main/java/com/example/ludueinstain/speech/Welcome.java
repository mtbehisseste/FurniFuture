package com.example.ludueinstain.speech;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.EditText;

public class Welcome extends AppCompatActivity {
//    public static final String EXTRA_IP = "null";
//    public static final String EXTRA_PORT = "null";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_welcome);
    }

    /* input ip and port */
    public void socketInformation(View view) {
        Intent intent = new Intent(this, MainActivity.class);
        EditText ipInput = findViewById(R.id.ipinput);
        EditText portInput = findViewById(R.id.portinput);
        String ip = ipInput.getText().toString();
        String port = portInput.getText().toString();

        intent.putExtra("EXTRA_IP", ip);
        intent.putExtra("EXTRA_PORT", port);

        startActivity(intent);
    }
}
