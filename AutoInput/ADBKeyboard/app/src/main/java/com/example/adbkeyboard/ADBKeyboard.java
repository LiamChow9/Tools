package com.example.adbkeyboard;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Base64;
import android.view.inputmethod.InputMethodManager;
import android.widget.Toast;
import java.nio.charset.StandardCharsets;

public class ADBKeyboard extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent.getAction() == null) return;

        switch (intent.getAction()) {
            case "ADB_INPUT_B64":
                String base64Text = intent.getStringExtra("msg");
                if (base64Text != null) {
                    try {
                        // Decode base64 text
                        byte[] decodedBytes = Base64.decode(base64Text, Base64.DEFAULT);
                        String decodedText = new String(decodedBytes, StandardCharsets.UTF_8);
                        
                        // Get the input method manager
                        InputMethodManager imm = (InputMethodManager) context.getSystemService(Context.INPUT_METHOD_SERVICE);
                        if (imm != null) {
                            // Send the decoded text
                            imm.sendText(decodedText);
                        }
                    } catch (Exception e) {
                        Toast.makeText(context, "Error decoding text: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                }
                break;
        }
    }
} 