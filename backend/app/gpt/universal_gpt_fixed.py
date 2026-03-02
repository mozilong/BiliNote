from app.gpt.base import GPT
from app.gpt.prompt_builder import generate_base_prompt
from app.models.gpt_model import GPTSource
from app.gpt.prompt import BASE_PROMPT, AI_SUM, SCREENSHOT, LINK
from app.gpt.utils import fix_markdown
from app.models.transcriber_model import TranscriptSegment
from datetime import timedelta
from typing import List


class UniversalGPT(GPT):
    def __init__(self, client, model: str, temperature: float = 0.7):
        self.client = client
        self.model = model
        self.temperature = temperature
        self.screenshot = False
        self.link = False

    def _format_time(self, seconds: float) -> str:
        return str(timedelta(seconds=int(seconds)))[2:]

    def _build_segment_text(self, segments: List[TranscriptSegment]) -> str:
        return "\n".join(
           f"{self._format_time(seg.start)} - {(seg.text or '').strip()}"
            for seg in segments
        )

    def ensure_segments_type(self, segments) -> List[TranscriptSegment]:
        return [TranscriptSegment(**seg) if isinstance(seg, dict) else seg for seg in segments]

    def create_messages(self, segments: List[TranscriptSegment], **kwargs):

        content_text = generate_base_prompt(
            title=kwargs.get('title'),
            segment_text=self._build_segment_text(segments),
            tags=kwargs.get('tags'),
            _format=kwargs.get('_format'),
            style=kwargs.get('style'),
            extras=kwargs.get('extras'),
        )

        # ⛳ 组装 content 数组，支持 text + image_url 混合
        content = [{"type": "text", "text": content_text}]
        video_img_urls = kwargs.get('video_img_urls', [])

        for url in video_img_urls:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": url,
                    "detail": "auto"
                }
            })

        #  正确格式：整体包在一个 message 里，role + content array
        messages = [{
            "role": "user",
            "content": content
        }]

        return messages

    def list_models(self):
        return self.client.models.list()

    def summarize(self, source: GPTSource) -> str:
        self.screenshot = source.screenshot
        self.link = source.link
        source.segment = self.ensure_segments_type(source.segment)
        if not source.segment:
            raise ValueError('Transcript is empty, cannot summarize.')

        max_chars = 60000

        def build_prompt(segs):
            return generate_base_prompt(
                title=source.title,
                segment_text=self._build_segment_text(segs),
                tags=source.tags,
                _format=source._format,
                style=source.style,
                extras=source.extras,
            )

        def is_len_err(exc):
            msg = str(exc).lower()
            return ('range of input length' in msg) or ('invalid_parameter_error' in msg)

        def call_messages(messages):
            rsp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )
            return (rsp.choices[0].message.content or '').strip()

        def safe_call(segs, with_images):
            kwargs = {
                'title': source.title,
                'tags': source.tags,
                'video_img_urls': source.video_img_urls if with_images else [],
                '_format': source._format,
                'style': source.style,
                'extras': source.extras,
            }
            try:
                return call_messages(self.create_messages(segs, **kwargs))
            except Exception as exc:
                if (not is_len_err(exc)) or len(segs) <= 1:
                    raise
                mid = len(segs) // 2
                left = safe_call(segs[:mid], False)
                right = safe_call(segs[mid:], False)
                return '\n\n'.join([x for x in [left, right] if x])

        def merge_texts(texts):
            texts = [x for x in texts if x and x.strip()]
            if not texts:
                return ''
            if len(texts) == 1:
                return texts[0]
            prompt = (
                'Merge these partial notes into one deduplicated markdown note. '
                'Keep key steps, conclusions, timeline and caveats.\n\n' + '\n\n'.join(texts)
            )
            msg = [{'role': 'user', 'content': [{'type': 'text', 'text': prompt}]}]
            try:
                return call_messages(msg)
            except Exception as exc:
                if (not is_len_err(exc)) or len(texts) <= 1:
                    raise
                mid = len(texts) // 2
                return merge_texts([merge_texts(texts[:mid]), merge_texts(texts[mid:])])

        if len(build_prompt(source.segment)) <= max_chars:
            return safe_call(source.segment, True)

        chunks, cur = [], []
        for seg in source.segment:
            cand = cur + [seg]
            if cur and len(build_prompt(cand)) > max_chars:
                chunks.append(cur)
                cur = [seg]
            else:
                cur = cand
        if cur:
            chunks.append(cur)

        partials = [safe_call(chunk, False) for chunk in chunks]
        while len(partials) > 1:
            grouped, buf, size = [], [], 0
            for text in partials:
                n = len(text)
                if buf and size + n > 30000:
                    grouped.append(merge_texts(buf))
                    buf, size = [text], n
                else:
                    buf.append(text)
                    size += n
            if buf:
                grouped.append(merge_texts(buf))
            partials = grouped

        return partials[0]
