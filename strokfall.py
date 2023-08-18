import streamlit as st
from PIL import Image  #pillow
import io
from io import BytesIO
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from collections import OrderedDict   #ordereddict
import mplstereonet
import base64   #pybase64


def trigger():
    st.title('Resultater')
    #st.markdown('Nedlastet har diagrammene bedre oppløsning enn det som vises her.')
    st.markdown(
        'Diagrammene kan også forstørres ved å holde over de og deretter trykke på utvid-knappen opp til høyre for diagrammet.')
    st.markdown('For å lage nye diagrammer er det bare å laste inn siden på nytt.')

    # Lager arrays for strøk og fall

    strok = []
    fall = []
    for g in range(antall * 2):
        if g >= antall:
            fall.append(st.session_state['{}'.format(g)])
        else:
            strok.append(st.session_state['{}'.format(g)])

    strikes = np.array(strok)
    dips = np.array(fall)

    # Lager diagrammene

    with st.container():
        st.write('')
        st.write('')
        bin_edges = np.arange(-5, 366, 10)
        number_of_strikes, bin_edges = np.histogram(strikes, bin_edges)
        number_of_strikes[0] += number_of_strikes[-1]
        half = np.sum(np.split(number_of_strikes[:-1], 2), 0)
        two_halves = np.concatenate([half, half])

        koll1, koll2 = st.columns(2)

        with koll1:
            # Sprekkerosen
            figsp = plt.figure(figsize=(14, 6))

            axsp = figsp.add_subplot(projection='polar')

            axsp.bar(np.deg2rad(np.arange(0, 360, 10)), two_halves, width=np.deg2rad(10), bottom=0.0, color='.8',
                     edgecolor='k')
            axsp.set_theta_zero_location('N')
            axsp.set_theta_direction(-1)
            axsp.set_thetagrids(np.arange(0, 360, 10), labels=np.arange(0, 360, 10))
            axsp.set_rgrids(np.arange(1, two_halves.max() + 1, 2), angle=0, weight='black')
            axsp.set_title('Sprekkerose', y=1.10, fontsize=12)
            axsp.grid()

            figsp.tight_layout()

            rose = io.BytesIO()
            plt.savefig(rose, format='JPEG')
            sprekkerose = Image.open(rose)

            st.image(sprekkerose)
            jpg_download_link(sprekkerose, 'sprekkerose.jpg')

        with koll2:
            # Polene
            figpol = plt.figure(figsize=(14, 6))

            axpol = figpol.add_subplot(projection='stereonet')

            axpol.pole(strikes, dips, c='k', label='Tetthet av polene')
            axpol.density_contourf(strikes, dips, measurement='poles', cmap='Reds')
            axpol.set_title('Tetthet av polene', y=1.10, fontsize=12)
            # axpol.grid()

            figpol.tight_layout()

            pol = io.BytesIO()
            plt.savefig(pol, format='JPEG')
            polene = Image.open(pol)

            st.image(polene)
            jpg_download_link(polene, 'tetthet_av_polene.jpg')

    # Lager stereonettene

    with st.container():
        st.write('')
        st.write('')
        st.write('')

        kolll1, kolll2 = st.columns(2)

        with kolll1:
            # Beta
            figbet = plt.figure(figsize=(14, 6))

            axbet = figbet.add_subplot(projection='stereonet')
            axbet.plane(strikes, dips, c='k', label='Plan')
            strike, dip = mplstereonet.fit_girdle(strikes, dips)
            axbet.pole(strike, dip, c='r', label='Beta-aksen')

            axbet.set_title('Beta diagram', y=1.10, fontsize=12)
            axbet.grid()

            handles, labels = axbet.get_legend_handles_labels()
            by_label = OrderedDict(zip(labels, handles))

            axbet.legend(by_label.values(), by_label.keys(), loc='upper left')

            figbet.tight_layout()

            stereo_bet = io.BytesIO()
            plt.savefig(stereo_bet, format='JPEG')
            betadiagram = Image.open(stereo_bet)

            st.image(betadiagram)
            jpg_download_link(betadiagram, 'beta_diagram.jpg')

        with kolll2:
            # S-pol
            figs = plt.figure(figsize=(14, 6))

            axs = figs.add_subplot(projection='stereonet')
            axs.pole(strikes, dips, c='k', label='Polene')
            axs.plane(strike, dip, c='g', label='Estimert storsirkel')
            axs.pole(strike, dip, c='r', label='Beta-aksen')

            axs.set_title('S-pol diagram', y=1.10, fontsize=12)
            axs.grid()

            handles, labels = axs.get_legend_handles_labels()
            by_label = OrderedDict(zip(labels, handles))

            axs.legend(by_label.values(), by_label.keys(), loc='upper left')

            figs.tight_layout()

            stereo_s = io.BytesIO()
            plt.savefig(stereo_s, format='JPEG')  # stereo_s.jpg
            spoldiagram = Image.open(stereo_s)

            st.image(spoldiagram)

            jpg_download_link(spoldiagram, 's-pol_diagram.jpg')

    # Tabeller for strøk og fall
    with st.container():
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.subheader('Dine data i tabell')

        data = {'Strøk': strok, 'Fall': fall}
        df = pd.DataFrame(data=data)
        st.write(df)

        excel_download_link(df)

    st.stop()


def jpg_download_link(img, filename):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/jpg;base64,{img_str}" download={filename}>Last ned som .jpg-fil</a>'
    return st.markdown(href, unsafe_allow_html=True)


def excel_download_link(df):
    towrite = BytesIO()
    df.to_excel(towrite, index=False, header=True) #encoding="utf-8"
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="strok_fall.xlsx">Last ned Excel-fil</a>'
    return st.markdown(href, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title='Sprekkerose og stereoplot', layout="wide", page_icon=':globe_with_meridians:')

    with st.container():
        kol1, kol2, kol4 = st.columns(3)
        with kol1:
            st.header('Sprekkerose og stereoplot')
            st.markdown(
                f'''
                Denne nettsiden lager diagrammer ut av strøk/fall-målinger. Etter å ha skrevet inn dine data blir du sendt til en ny side med dine resultater.\n
                Diagrammene som blir laget er:
                * Sprekkerose
                * Tetthetsplott av polene
                * Beta diagram
                * S-pol diagram
                Alle diagrammene kan lastes ned som .jpg-filer.\n
                En tabell av dine data blir også laget, denne kan lastes ned som en Excel-fil. (.xlsx)\n
                **OBS:** Pass på at du skriver inn rett antall målinger, tabellen må fylles inn på nytt om antall målinger endres.

                ''')
        with kol4:
            av_logo = Image.open('av-logo.png')
            st.image(av_logo, caption=None, width=500)

    with st.container():
        st.write('')
        st.write('')
        global antall
        antall = st.number_input('Hvor mange målinger av strøk/fall har du?', min_value=1, max_value=100, value=1,
                                 step=1)
        form = st.form(key='antall')
        submit = form.form_submit_button(label='Lag tabell')

    if submit:
        with st.form(key='kalkuler'):
            col1, col2 = st.columns(2)
            with col1:
                for i in range(antall):
                    st.number_input('Strøk', min_value=0, max_value=360, value=0, step=1, key=i)

            with col2:
                for i in range(antall):
                    st.number_input('Fall', min_value=0, max_value=90, value=0, step=1, key=antall + i)

            st.form_submit_button(label='Kalkuler', on_click=trigger)


if __name__ == '__main__':
    main()
