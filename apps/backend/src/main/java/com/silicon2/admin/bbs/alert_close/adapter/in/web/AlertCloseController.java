package com.silicon2.admin.bbs.alert_close.adapter.in.web;

import org.springframework.http.MediaType;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
@RequestMapping("/v1/admin/bbs/alert-close")
public class AlertCloseController {

    @GetMapping(produces = MediaType.TEXT_HTML_VALUE)
    @ResponseBody
    public String renderAlertClose(
            @RequestParam(required = false) String msg,
            @RequestParam(required = false) String error) {

        String message = msg != null ? msg : "작업이 완료되었습니다.";
        boolean isError = "true".equals(error) || "1".equals(error);

        // Escape message for JavaScript string literal (handle quotes and backslashes)
        String escapedMsg = message.replace("\\", "\\\\")
                                   .replace("\"", "\\\"")
                                   .replace("'", "\\'")
                                   .replace("\r", "")
                                   .replace("\\n", "\n");

        // For HTML display, convert literal \n to <br>
        String htmlMessage = message.replace("\\n", "<br>");

        String alertClass = isError ? "error" : "success";
        String alertTitle = isError ? "오류" : "확인";

        return "<!DOCTYPE html>\n" +
               "<html lang=\"ko\">\n" +
               "<head>\n" +
               "  <meta charset=\"UTF-8\">\n" +
               "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n" +
               "  <title>" + alertTitle + "</title>\n" +
               "  <style>\n" +
               "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f9fafb; }\n" +
               "    #validation_check { max-width: 600px; margin: 40px auto; background: white; border-radius: 8px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }\n" +
               "    h1 { font-size: 20px; font-weight: 600; margin: 0 0 16px 0; color: #111827; }\n" +
               "    .cbg { font-size: 14px; line-height: 1.6; color: #374151; margin: 8px 0; }\n" +
               "    .error h1 { color: #dc2626; }\n" +
               "    .success h1 { color: #059669; }\n" +
               "  </style>\n" +
               "</head>\n" +
               "<body>\n" +
               "<script>\n" +
               "  alert(\"" + escapedMsg + "\");\n" +
               "  window.close();\n" +
               "  setTimeout(function() {\n" +
               "    if (window.opener) window.opener.focus();\n" +
               "    window.close();\n" +
               "  }, 100);\n" +
               "</script>\n" +
               "<noscript>\n" +
               "  <div id=\"validation_check\" class=\"" + alertClass + "\">\n" +
               "    <h1>" + alertTitle + "</h1>\n" +
               "    <p class=\"cbg\">" + htmlMessage + "</p>\n" +
               "    <p class=\"cbg\">새 창을 닫으신 후 서비스를 이용해 주세요.</p>\n" +
               "  </div>\n" +
               "</noscript>\n" +
               "</body>\n" +
               "</html>";
    }
}
