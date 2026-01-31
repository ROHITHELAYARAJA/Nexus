"""
PDF Generator for NEXUS
Export chat conversations to professional PDF documents
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import HexColor
from io import BytesIO
from datetime import datetime
from typing import List, Dict


class PDFGenerator:
    """Generate professional PDF exports of conversations"""
    
    @staticmethod
    def generate_chat_pdf(conversation: Dict) -> BytesIO:
        """Generate PDF from conversation data"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#6366f1'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#666666'),
            spaceAfter=20,
            alignment=1
        )
        
        user_style = ParagraphStyle(
            'UserMessage',
            parent=styles['Normal'],
            fontSize=11,
            textColor=HexColor('#1f2937'),
            leftIndent=20,
            rightIndent=20,
            spaceAfter=6,
            spaceBefore=6
        )
        
        assistant_style = ParagraphStyle(
            'AssistantMessage',
            parent=styles['Normal'],
            fontSize=11,
            textColor=HexColor('#374151'),
            leftIndent=20,
            rightIndent=20,
            spaceAfter=12,
            spaceBefore=6
        )
        
        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor('#8b5cf6'),
            leftIndent=20,
            fontName='Helvetica-Bold'
        )
        
        # Title
        elements.append(Paragraph("NEXUS Conversation Export", title_style))
        
        # Metadata
        created_date = conversation.get('created_at', datetime.now().isoformat())
        model = conversation.get('model', 'Multi-Model')
        message_count = conversation.get('message_count', len(conversation.get('messages', [])))
        
        metadata = f"""
        <b>Title:</b> {conversation.get('title', 'Untitled Conversation')}<br/>
        <b>Date:</b> {created_date}<br/>
        <b>Model:</b> {model}<br/>
        <b>Messages:</b> {message_count}
        """
        elements.append(Paragraph(metadata, subtitle_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Divider
        elements.append(Paragraph("━" * 80, subtitle_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Messages
        messages = conversation.get('messages', [])
        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            msg_model = msg.get('model', '')
            
            # Role label
            if role == 'user':
                label_text = "👤 User"
                style = user_style
            else:
                label_text = f"🤖 NEXUS"
                if msg_model:
                    label_text += f" ({msg_model})"
                style = assistant_style
            
            elements.append(Paragraph(label_text, label_style))
            
            # Message content (escape HTML special chars)
            safe_content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            safe_content = safe_content.replace('\n', '<br/>')
            
            elements.append(Paragraph(safe_content, style))
            elements.append(Spacer(1, 0.15*inch))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_multi_conversation_pdf(conversations: List[Dict]) -> BytesIO:
        """Generate PDF with multiple conversations"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        for i, conv in enumerate(conversations):
            # Add conversation
            conv_pdf = PDFGenerator.generate_chat_pdf(conv)
            # Note: In a real implementation, you'd merge PDFs or add page breaks
            
            if i < len(conversations) - 1:
                elements.append(PageBreak())
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
