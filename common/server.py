from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import widget
import utils
from config import config

logger = utils.getLogger()

app = FastAPI()

file_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(file_dir, "templates"))  # Ensure your template.html is in the 'templates' directory


@app.get('/', response_class=HTMLResponse)
async def get_website(request: Request):
    logger.info('Create main website')
    return templates.TemplateResponse('template.html',
                                      {'request': request, 'apps': config.apps, 'active_app': config.active_app})


@app.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    upload_image_path = os.path.join(os.path.dirname(__file__), 'upload.png')
    try:
        with open(upload_image_path, 'wb') as f:
            f.write(await file.read())
        logger.info(f'Upload image to {upload_image_path}')
        widget.update(upload_image_path)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'message': 'Image uploaded successfully'},
        )
    except Exception as e:
        logger.error(f'File upload failed: {e}', exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': 'File upload failed: {e}'},
        )


@app.post('/apps/{app_id}')
async def handle_app_form(app_id: str, request: Request):
    form_data = await request.form()
    fields = {key: value for key, value in form_data.items()}
    logger.info(f'Received form data for app_id={app_id}: {fields}')
    try:
        app = config.get_app(app_id)
        if app:
            app.parameter = fields
            app.general = fields
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={'message': f'App Settings updated for {app_id}'},
            )
        else:
            logger.warning(f'Invalid App Requested! app_id: {app_id}')
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={'detail': f'Invalid App Requested! app_id: {app_id}'},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'detail': f'Request failed {e}'},
        )


@app.post('/general/save')
async def handle_general_form_save(active_app: str = Form(None)):
    logger.info('Button pressed in form "general"->"save"')
    if not active_app:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'detail': 'active_app is required'},
        )
    logger.info(f'Set active app: {active_app}')
    config.active_app = active_app
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'message': f'Set active app to {active_app}'},
    )


@app.post('/general/update', )
async def handle_general_form_save():
    logger.info('Button pressed in form "general"->"update"')
    widget.update()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'message': f'Update {config.active_app}'},
    )


# Static files (optional, for serving styles or other assets)
app.mount('/static', StaticFiles(directory=os.path.join(file_dir, 'templates', 'static')), name='static')

if __name__ == '__main__':
    import uvicorn

    port = 8000
    logger.info(f'Open Browser: {utils.get_network_ip()}:{port}')
    uvicorn.run(app, host='0.0.0.0', port=port)
